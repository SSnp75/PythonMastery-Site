"""Voting routes."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class VoteCreate(BaseModel):
    value: int  # +1 or -1


@router.post("/questions/{target_id}")
async def vote_question(target_id: int, data: VoteCreate):
    """Upvote/downvote a question."""
    return {"target_type": "question", "target_id": target_id, "value": data.value}


@router.post("/answers/{target_id}")
async def vote_answer(target_id: int, data: VoteCreate):
    """Upvote/downvote an answer."""
    return {"target_type": "answer", "target_id": target_id, "value": data.value}
