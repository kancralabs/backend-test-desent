"""Book repository - Data access layer with optimized cursor pagination"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import CursorPage, apply_cursor_filter, encode_cursor
from app.models.book import Book


class BookRepository:
    """
    Repository pattern for Book model.

    Provides data access methods with optimized queries for high performance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, book: Book) -> Book:
        """Create a new book in database"""
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def get_by_id(self, book_id: UUID) -> Optional[Book]:
        """Get book by ID"""
        result = await self.db.execute(select(Book).where(Book.id == book_id))
        return result.scalar_one_or_none()

    async def update(self, book: Book) -> Book:
        """Update existing book"""
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete(self, book: Book) -> None:
        """Delete book"""
        await self.db.delete(book)
        await self.db.commit()

    async def list_paginated(
        self, limit: int = 10, cursor: Optional[str] = None, author: Optional[str] = None
    ) -> CursorPage[Book]:
        """
        List books with cursor-based pagination and optional filtering.

        PERFORMANCE CRITICAL:
        - Uses idx_books_created_at for unfiltered pagination
        - Uses idx_books_author_created for filtered pagination
        - Fetches limit+1 to determine has_more without separate COUNT query
        - O(log n) complexity regardless of page depth

        Args:
            limit: Maximum number of items to return
            cursor: Encoded cursor for pagination
            author: Optional author name filter

        Returns:
            CursorPage with books and pagination metadata
        """
        query = select(Book)

        # Filter by author (uses idx_books_author_created composite index)
        if author:
            query = query.where(Book.author == author)

        # Apply cursor pagination (uses idx_books_created_at or composite index)
        query = apply_cursor_filter(query, Book, cursor)

        # Fetch limit+1 to check if more results exist
        query = query.limit(limit + 1)

        result = await self.db.execute(query)
        books = list(result.scalars().all())

        # Determine if there are more results
        has_more = len(books) > limit
        if has_more:
            books = books[:limit]  # Trim to requested limit

        # Generate next cursor from last item
        next_cursor = None
        if books and has_more:
            last_book = books[-1]
            next_cursor = encode_cursor(last_book.created_at, str(last_book.id))

        return CursorPage(items=books, next_cursor=next_cursor, has_more=has_more)
