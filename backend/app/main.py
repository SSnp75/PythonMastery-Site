"""Python Mastery Q&A Backend — FastAPI Application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, questions, answers, comments, votes, search

app = FastAPI(
    title="Python Mastery Q&A API",
    description="Q&A system for the Python Mastery learning platform",
    version="0.1.0",
)

# CORS — allow the static site to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pythonmastery.dev",
        "http://127.0.0.1:8000",   # local MkDocs dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(questions.router, prefix="/api/v1/questions", tags=["questions"])
app.include_router(answers.router, prefix="/api/v1/answers", tags=["answers"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["comments"])
app.include_router(votes.router, prefix="/api/v1/votes", tags=["votes"])
app.include_router(search.router, prefix="/api/v1/search", tags=["search"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
