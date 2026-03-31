"""Book CRUD endpoints - Level 3, 4, 6 with authentication"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.pagination import CursorPage
from app.core.security import verify_token
from app.dependencies import get_book_service
from app.schemas.book import BookCreate, BookResponse, BookUpdate
from app.services.book_service import BookService

router = APIRouter(prefix="/books", tags=["books"])


@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_token)],
)
async def create_book(
    data: BookCreate,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """
    Level 3: Create a new book.

    Requires authentication (Level 5).

    Args:
        data: Book creation data
        service: Injected book service

    Returns:
        Created book with ID and timestamps

    Raises:
        401: If not authenticated
        422: If validation fails
    """
    return await service.create_book(data)


@router.get(
    "",
    response_model=CursorPage[BookResponse],
    dependencies=[Depends(verify_token)],
)
async def list_books(
    limit: int = Query(10, ge=1, le=100, description="Number of items per page"),
    cursor: Optional[str] = Query(None, description="Pagination cursor for next page"),
    author: Optional[str] = Query(None, description="Filter by author name"),
    service: BookService = Depends(get_book_service),
) -> CursorPage[BookResponse]:
    """
    Level 3 + Level 6: List books with cursor pagination and filtering.

    Requires authentication (Level 5).

    Features:
    - Cursor-based pagination (performance-optimized for 1M+ rows)
    - Author filtering
    - Deterministic ordering (created_at DESC, id ASC)

    Query parameters:
    - limit: Number of items to return (1-100, default: 10)
    - cursor: Encoded cursor from previous response's next_cursor
    - author: Filter books by exact author name

    Example requests:
    - /books?limit=10 (first page)
    - /books?cursor=eyJjcmVhdGVkX2F0IjoiMjAyNC4uLg==&limit=10 (next page)
    - /books?author=Robert%20Martin&limit=20 (filtered by author)

    Returns:
        Paginated response with:
        - items: List of books
        - next_cursor: Cursor for next page (null if no more results)
        - has_more: Boolean indicating if more results exist

    Raises:
        401: If not authenticated
    """
    return await service.list_books(limit=limit, cursor=cursor, author=author)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    dependencies=[Depends(verify_token)],
)
async def get_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """
    Level 3: Get a single book by ID.

    Requires authentication (Level 5).

    Args:
        book_id: Book UUID
        service: Injected book service

    Returns:
        Book details

    Raises:
        401: If not authenticated
        404: If book not found
    """
    return await service.get_book(book_id)


@router.put(
    "/{book_id}",
    response_model=BookResponse,
    dependencies=[Depends(verify_token)],
)
async def update_book(
    book_id: UUID,
    data: BookUpdate,
    service: BookService = Depends(get_book_service),
) -> BookResponse:
    """
    Level 4: Update a book (partial update supported).

    Requires authentication (Level 5).

    Only fields present in request will be updated.
    Omitted fields remain unchanged.

    Args:
        book_id: Book UUID
        data: Book update data
        service: Injected book service

    Returns:
        Updated book

    Raises:
        401: If not authenticated
        404: If book not found
        422: If validation fails
    """
    return await service.update_book(book_id, data)


@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_token)],
)
async def delete_book(
    book_id: UUID,
    service: BookService = Depends(get_book_service),
) -> None:
    """
    Level 4: Delete a book.

    Requires authentication (Level 5).

    Args:
        book_id: Book UUID
        service: Injected book service

    Returns:
        No content (204)

    Raises:
        401: If not authenticated
        404: If book not found
    """
    await service.delete_book(book_id)
