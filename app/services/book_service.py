"""Book service - Business logic layer"""
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status

from app.core.pagination import CursorPage
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookCreate, BookResponse, BookUpdate


class BookService:
    """
    Service layer for book operations.

    Handles business logic, validation, and error handling.
    """

    def __init__(self, repository: BookRepository):
        self.repository = repository

    async def create_book(self, data: BookCreate) -> BookResponse:
        """
        Create a new book.

        Args:
            data: Book creation data

        Returns:
            Created book

        Raises:
            HTTPException: If validation fails (422)
        """
        # Business rule: Validate published_year range
        if data.published_year and not (1000 <= data.published_year <= 2100):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Published year must be between 1000 and 2100",
            )

        book = Book(**data.model_dump())
        created_book = await self.repository.create(book)
        return BookResponse.model_validate(created_book)

    async def get_book(self, book_id: UUID) -> BookResponse:
        """
        Get book by ID.

        Args:
            book_id: Book UUID

        Returns:
            Book details

        Raises:
            HTTPException: If book not found (404)
        """
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found"
            )
        return BookResponse.model_validate(book)

    async def update_book(self, book_id: UUID, data: BookUpdate) -> BookResponse:
        """
        Update book (partial update supported).

        Args:
            book_id: Book UUID
            data: Book update data (only non-None fields are updated)

        Returns:
            Updated book

        Raises:
            HTTPException: If book not found (404) or validation fails (422)
        """
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found"
            )

        # Apply partial updates (only fields that are set in request)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)

        updated_book = await self.repository.update(book)
        return BookResponse.model_validate(updated_book)

    async def delete_book(self, book_id: UUID) -> None:
        """
        Delete book.

        Args:
            book_id: Book UUID

        Raises:
            HTTPException: If book not found (404)
        """
        book = await self.repository.get_by_id(book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Book with id {book_id} not found"
            )
        await self.repository.delete(book)

    async def list_books(
        self, limit: int = 10, cursor: Optional[str] = None, author: Optional[str] = None
    ) -> CursorPage[BookResponse]:
        """
        List books with cursor pagination and optional filtering.

        Args:
            limit: Maximum number of items to return (1-100)
            cursor: Encoded cursor for pagination
            author: Optional author name filter

        Returns:
            Paginated list of books
        """
        page = await self.repository.list_paginated(limit, cursor, author)

        # Convert ORM models to Pydantic response schemas
        return CursorPage(
            items=[BookResponse.model_validate(book) for book in page.items],
            next_cursor=page.next_cursor,
            has_more=page.has_more,
        )
