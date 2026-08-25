"""Question CRUD routes."""
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()


class QuestionCreate(BaseModel):
    page_path: str
    title: str
    body: str
    tags: list[str] = []


class QuestionResponse(BaseModel):
    id: int
    page_path: str
    title: str
    body: str
    tags: list[str]
    vote_count: int
    answer_count: int
    author: dict
    created_at: str


@router.get("/")
async def list_questions(
    page_path: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """List questions, optionally filtered by page_path."""
    # TODO: query DB with filters and pagination
    return {"questions": [], "total": 0, "page": page}


@router.post("/", status_code=201)
async def create_question(data: QuestionCreate):
    """Create a new question (auth required)."""
    # TODO: validate auth, create question, return
    return {"id": 1, "title": data.title}


@router.get("/{question_id}")
async def get_question(question_id: int):
    """Get question detail with answers."""
    # TODO: fetch question + answers + comments
    return {"id": question_id, "title": "...", "answers": []}


@router.patch("/{question_id}")
async def update_question(question_id: int, data: QuestionCreate):
    """Edit a question (author only)."""
    return {"id": question_id, "updated": True}


@router.delete("/{question_id}", status_code=204)
async def delete_question(question_id: int):
    """Delete a question (author/admin only)."""
    return None
