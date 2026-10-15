from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks

from sqlalchemy import text
from pydantic import BaseModel

from backend.api.study import router as study_router
from backend.api.documents import router as documents_router

from backend.database.connection import engine

from backend.services.hierarchical_roadmap import (
    generate_hierarchical_roadmap
)

from backend.services.document_processor import (
    process_document,
    process_and_store_document
)

from backend.services.vector_store import (
    save_document,
    update_document_status
)


# ========================================
# FastAPI application
# ========================================

app = FastAPI(
    title="AI Study Companion API",
    description="Backend API for AI Study Companion",
    version="1.0.0"
)


# ========================================
# CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Routers
# ========================================

app.include_router(study_router)
app.include_router(documents_router)


# ========================================
# Upload directory
# ========================================

UPLOAD_DIR = Path("data/uploads")

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ========================================
# Root
# ========================================

@app.get("/")
def root():

    return {
        "message": "AI Study Companion API is running"
    }


# ========================================
# Health check
# ========================================

@app.get("/api/health")
def health_check():

    return {
        "status": "healthy"
    }


# ========================================
# Generate learning roadmap
# ========================================

class RoadmapRequest(BaseModel):
    document_id: int


@app.post("/api/roadmap/generate")
def create_roadmap(request: RoadmapRequest):

    print(
        f"Starting hierarchical roadmap generation "
        f"for document {request.document_id}"
    )

    try:

        roadmap = generate_hierarchical_roadmap(
            document_id=request.document_id
        )

        return {
            "success": True,
            "roadmap": roadmap
        }

    except Exception as error:

        print(
            f"Roadmap generation failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )



# ========================================
# Background document processing
# ========================================

def process_uploaded_document(
    file_path: Path,
    document_id: int
):
    """
    Process an uploaded document in the background.

    The existing document_id is passed through so
    processing updates the correct database record.
    """

    try:

        print(
            f"Starting processing for document "
            f"{document_id}"
        )

        # ------------------------------------
        # Mark as processing
        # ------------------------------------

        update_document_status(
            document_id,
            status="processing",
            processed_chunks=0,
            error_message=None
        )

        # ------------------------------------
        # Extract document text
        # ------------------------------------

        pages = process_document(
            file_path,
            document_id=document_id
        )

        print(
            f"Document {document_id}: "
            f"extracted {len(pages)} pages"
        )

        # ------------------------------------
        # Process and store
        # ------------------------------------

        result = process_and_store_document(
            file_path,
            pages,
            document_id=document_id
        )

        print(
            f"Document {document_id} completed: "
            f"{result['chunks']} chunks"
        )

    except Exception as error:

        print(
            f"Document {document_id} failed: "
            f"{error}"
        )

        update_document_status(
            document_id,
            status="failed",
            error_message=str(error)
        )


# ========================================
# Upload document
# ========================================

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):

    # ----------------------------------------
    # Validate filename
    # ----------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No filename provided."
        )

    # ----------------------------------------
    # Allowed file types
    # ----------------------------------------

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".pptx",
        ".txt"
    }

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Use PDF, DOCX, PPTX, or TXT."
            )
        )

    # ----------------------------------------
    # Create safe filename
    # ----------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    file_path = (
        UPLOAD_DIR / safe_filename
    )

    # ----------------------------------------
    # Save uploaded file
    # ----------------------------------------

    try:

        with file_path.open("wb") as buffer:

            while True:

                chunk = await file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                buffer.write(chunk)

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not save file: {error}"
            )
        )

    finally:

        await file.close()

    # ----------------------------------------
    # Create ONE document record
    # ----------------------------------------

    try:

        document_id = save_document(
            filename=safe_filename,
            file_type=extension
        )

        # ------------------------------------
        # Immediately mark as processing
        # ------------------------------------

        update_document_status(
            document_id,
            status="processing",
            total_chunks=0,
            processed_chunks=0,
            error_message=None
        )

    except Exception as error:

        # Remove uploaded file if database
        # record creation fails.

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Could not create document record: "
                f"{error}"
            )
        )

    # ----------------------------------------
    # Start background processing
    # ----------------------------------------

    background_tasks.add_task(
        process_uploaded_document,
        file_path,
        document_id
    )

    # ----------------------------------------
    # Return immediately
    # ----------------------------------------

    return {
        "message": "File uploaded successfully.",
        "document_id": document_id,
        "filename": safe_filename,
        "file_type": extension,
        "status": "processing"
    }


# ========================================
# Get document processing status
# ========================================

@app.get("/api/documents/{document_id}/status")
def get_document_status(document_id: int):

    query = text("""
        SELECT
            id,
            filename,
            file_type,
            status,
            processing_stage,
            current_page,
            total_pages,
            total_chunks,
            processed_chunks,
            error_message
        FROM documents
        WHERE id = :document_id;
    """)

    with engine.connect() as connection:

        result = connection.execute(
            query,
            {
                "document_id": document_id
            }
        )

        document = result.mappings().first()

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    # ----------------------------------------
    # Chunk progress
    # ----------------------------------------

    total_chunks = document["total_chunks"] or 0

    processed_chunks = (
        document["processed_chunks"] or 0
    )

    if total_chunks > 0:

        progress = round(
            (processed_chunks / total_chunks) * 100,
            2
        )

    else:

        progress = 0

    # ----------------------------------------
    # Page progress
    # ----------------------------------------

    total_pages = document["total_pages"] or 0

    current_page = document["current_page"] or 0

    if total_pages > 0:

        page_progress = round(
            (current_page / total_pages) * 100,
            2
        )

    else:

        page_progress = 0

    # ----------------------------------------
    # Return status
    # ----------------------------------------

    return {
        "document_id": document["id"],
        "filename": document["filename"],
        "file_type": document["file_type"],
        "status": document["status"],
        "processing_stage": document["processing_stage"],
        "current_page": current_page,
        "total_pages": total_pages,
        "page_progress": page_progress,
        "total_chunks": total_chunks,
        "processed_chunks": processed_chunks,
        "progress": progress,
        "error": document["error_message"]
    }