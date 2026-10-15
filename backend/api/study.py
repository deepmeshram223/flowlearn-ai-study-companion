from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.services.rag import answer_question


router = APIRouter(
    prefix="/api/study",
    tags=["Study"]
)


class QuestionRequest(BaseModel):
    question: str
    document_id: int
    limit: int = 5


@router.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:

        result = answer_question(
            question=question,
            document_id=request.document_id,
            limit=request.limit
        )

        return result

    except Exception as error:

        print(
            f"Question answering failed: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate an answer."
        )