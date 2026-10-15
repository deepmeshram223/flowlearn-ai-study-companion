from fastapi import APIRouter
from sqlalchemy import text

from backend.database.connection import engine


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"]
)


@router.get("")
def get_documents():
    query = text("""
        SELECT
            id,
            filename,
            file_type,
            status,
            processing_stage,
            total_chunks,
            processed_chunks,
            error_message,
            created_at
        FROM documents
        ORDER BY created_at DESC;
    """)

    with engine.connect() as connection:
        result = connection.execute(query)

        documents = []

        for row in result:
            documents.append({
                "id": row.id,
                "filename": row.filename,
                "file_type": row.file_type,
                "status": row.status,
                "processing_stage": row.processing_stage,
                "total_chunks": row.total_chunks,
                "processed_chunks": row.processed_chunks,
                "error_message": row.error_message,
                "created_at": row.created_at.isoformat()
                if row.created_at
                else None,
            })

    return documents