from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.hierarchical_roadmap import (
    generate_hierarchical_roadmap,
)

router = APIRouter(
    prefix="/api/roadmap",
    tags=["Roadmap"],
)


class RoadmapRequest(BaseModel):
    document_id: int


@router.post("/generate")
def generate_roadmap(request: RoadmapRequest):
    try:
        roadmap = generate_hierarchical_roadmap(
            document_id=request.document_id
        )

        return {
            "success": True,
            "roadmap": roadmap,
        }

    except Exception as error:
        print(f"Roadmap generation failed: {error}")

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )