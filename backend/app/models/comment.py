from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class Comment(Base, TimestampMixin):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    parent_type: Mapped[str] = mapped_column(String(20))  # "question" or "answer"
    parent_id: Mapped[int] = mapped_column()
    body: Mapped[str] = mapped_column(Text)

    def __repr__(self):
        return f"Comment(id={self.id}, on={self.parent_type}:{self.parent_id})"
