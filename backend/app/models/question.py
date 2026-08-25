from sqlalchemy import String, Text, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    page_path: Mapped[str] = mapped_column(String(300), index=True)  # e.g. "core/intermediate/decorators"
    title: Mapped[str] = mapped_column(String(500))
    body: Mapped[str] = mapped_column(Text)  # Markdown
    tags: Mapped[str] = mapped_column(Text, default="")  # comma-separated tags
    vote_count: Mapped[int] = mapped_column(default=0)
    answer_count: Mapped[int] = mapped_column(default=0)
    accepted_answer_id: Mapped[int | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open")  # open, closed, resolved

    # Relationships
    author: Mapped["User"] = relationship(back_populates="questions")
    answers: Mapped[list["Answer"]] = relationship(back_populates="question", cascade="all, delete-orphan")

    def __repr__(self):
        return f"Question(id={self.id}, title={self.title!r})"
