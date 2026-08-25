from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class TimestampMixin:
    """Adds created_at and updated_at to any model."""
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())
