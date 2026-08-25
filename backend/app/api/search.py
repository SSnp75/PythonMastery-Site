"""Search routes."""
from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def search_questions(
    q: str = Query(..., min_length=2, max_length=200),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    """Full-text search across questions and answers."""
    # TODO: PostgreSQL full-text search or Elasticsearch
    return {"results": [], "total": 0, "query": q, "page": page}
