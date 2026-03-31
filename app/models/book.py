"""Book ORM model with performance-critical indexes"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Book(Base):
    """
    Book model representing a book in the library.

    Performance optimizations:
    - UUID primary key for distributed-safe IDs
    - Descending index on created_at for efficient cursor pagination
    - Composite index on (author, created_at) for filtered pagination
    """

    __tablename__ = "books"

    # Columns
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # PERFORMANCE CRITICAL: Indexes for sub-50ms queries at 1M+ rows
    __table_args__ = (
        # Descending index on created_at for efficient ORDER BY in cursor pagination
        Index(
            "idx_books_created_at",
            "created_at",
            postgresql_ops={"created_at": "DESC"},
        ),
        # Index on author for filtering
        Index("idx_books_author", "author"),
        # Composite index for filtered pagination (e.g., ?author=X with cursor)
        Index(
            "idx_books_author_created",
            "author",
            "created_at",
            postgresql_ops={"created_at": "DESC"},
        ),
    )

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title!r}, author={self.author!r})>"
