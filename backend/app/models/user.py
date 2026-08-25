from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    github_id: Mapped[int] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    display_name: Mapped[str] = mapped_column(String(200))
    avatar_url: Mapped[str] = mapped_column(String(500), default="")
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reputation: Mapped[int] = mapped_column(default=0)
    role: Mapped[str] = mapped_column(String(20), default="user")  # user, moderator, admin

    # Relationships
    questions: Mapped[list["Question"]] = relationship(back_populates="author")
    answers: Mapped[list["Answer"]] = relationship(back_populates="author")

    def __repr__(self):
        return f"User(id={self.id}, username={self.username!r})"
