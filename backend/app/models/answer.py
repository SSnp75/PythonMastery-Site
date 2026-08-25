from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class Answer(Base, TimestampMixin):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)  # Markdown
    vote_count: Mapped[int] = mapped_column(default=0)
    is_accepted: Mapped[bool] = mapped_column(default=False)

    # Relationships
    question: Mapped["Question"] = relationship(back_populates="answers")
    author: Mapped["User"] = relationship(back_populates="answers")

    def __repr__(self):
        return f"Answer(id={self.id}, question_id={self.question_id})"
