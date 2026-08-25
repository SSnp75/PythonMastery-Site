"""Comment routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CommentCreate(BaseModel):
    body: str


@router.post("/questions/{parent_id}/comments", status_code=201)
async def comment_on_question(parent_id: int, data: CommentCreate):
    return {"id": 1, "parent_type": "question", "body": data.body}


@router.post("/answers/{parent_id}/comments", status_code=201)
async def comment_on_answer(parent_id: int, data: CommentCreate):
    return {"id": 1, "parent_type": "answer", "body": data.body}


@router.delete("/{comment_id}", status_code=204)
async def delete_comment(comment_id: int):
    return None
