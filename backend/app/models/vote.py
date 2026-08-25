from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin


class Vote(Base, TimestampMixin):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("user_id", "target_type", "target_id", name="uq_user_target"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    target_type: Mapped[str] = mapped_column(String(20))  # "question" or "answer"
    target_id: Mapped[int] = mapped_column()
    value: Mapped[int] = mapped_column()  # +1 or -1

    def __repr__(self):
        return f"Vote(user={self.user_id}, {self.target_type}:{self.target_id}, {self.value:+d})"
