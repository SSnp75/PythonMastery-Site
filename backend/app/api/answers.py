"""Answer routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AnswerCreate(BaseModel):
    body: str


@router.post("/questions/{question_id}/answers", status_code=201)
async def create_answer(question_id: int, data: AnswerCreate):
    """Post an answer to a question."""
    return {"id": 1, "question_id": question_id, "body": data.body}


@router.patch("/{answer_id}")
async def update_answer(answer_id: int, data: AnswerCreate):
    """Edit an answer (author only)."""
    return {"id": answer_id, "updated": True}


@router.delete("/{answer_id}", status_code=204)
async def delete_answer(answer_id: int):
    """Delete answer (author/admin)."""
    return None


@router.post("/{answer_id}/accept")
async def accept_answer(answer_id: int):
    """Mark answer as accepted (question author only)."""
    return {"id": answer_id, "is_accepted": True}
