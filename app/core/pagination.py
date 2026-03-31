"""Cursor-based pagination utilities for high-performance queries"""
import base64
import json
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict
from sqlalchemy import and_, or_

T = TypeVar("T")


class CursorPage(BaseModel, Generic[T]):
    """
    Generic paginated response with cursor.

    Attributes:
        items: List of items in current page
        next_cursor: Encoded cursor for next page (None if no more items)
        has_more: Boolean indicating if more items exist
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    items: List[T]
    next_cursor: Optional[str] = None
    has_more: bool = False


class CursorParams(BaseModel):
    """
    Decoded cursor parameters.

    Attributes:
        created_at: Timestamp from cursor
        id: UUID string for tie-breaking (ensures deterministic ordering)
    """

    created_at: datetime
    id: str


def encode_cursor(created_at: datetime, id: str) -> str:
    """
    Encode cursor to hide implementation details.

    Encodes (created_at, id) as base64-encoded JSON.

    Args:
        created_at: Timestamp for pagination
        id: UUID string for tie-breaking

    Returns:
        Base64-encoded cursor string

    Example:
        >>> encode_cursor(datetime(2024, 1, 15), "uuid-here")
        "eyJjcmVhdGVkX2F0IjoiMjAyNC0wMS0xNVQwMDowMDowMCIsImlkIjoidXVpZC1oZXJlIn0="
    """
    cursor_data = {
        "created_at": created_at.isoformat(),
        "id": str(id),
    }
    json_str = json.dumps(cursor_data, separators=(",", ":"))
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> CursorParams:
    """
    Decode cursor to extract pagination parameters.

    Args:
        cursor: Base64-encoded cursor string

    Returns:
        Decoded cursor parameters

    Raises:
        ValueError: If cursor is malformed or invalid
    """
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        data = json.loads(json_str)
        return CursorParams(created_at=datetime.fromisoformat(data["created_at"]), id=data["id"])
    except (ValueError, KeyError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid cursor format: {e}")


def apply_cursor_filter(query, model, cursor: Optional[str]):
    """
    Apply cursor-based WHERE clause to SQLAlchemy query.

    Implements stable cursor pagination using (created_at, id) composite:
    - ORDER BY created_at DESC, id ASC
    - WHERE (created_at < cursor_time) OR (created_at = cursor_time AND id > cursor_id)

    Performance:
    - Uses indexed columns (idx_books_created_at, idx_books_author_created)
    - O(log n) complexity regardless of page depth
    - No OFFSET scan penalty

    Args:
        query: SQLAlchemy select query
        model: SQLAlchemy model class (e.g., Book)
        cursor: Optional encoded cursor string

    Returns:
        Modified query with cursor filtering and ordering applied

    Example:
        >>> query = select(Book)
        >>> query = apply_cursor_filter(query, Book, cursor="eyJ...")
        >>> # Generates: WHERE (created_at < '2024-01-15') OR (created_at = '2024-01-15' AND id > 'uuid')
        >>> #           ORDER BY created_at DESC, id ASC
    """
    # Always order by created_at DESC, id ASC for consistent pagination
    query = query.order_by(model.created_at.desc(), model.id.asc())

    if cursor:
        params = decode_cursor(cursor)
        # Cursor filter: show items before this cursor position
        # Uses (created_at, id) composite for deterministic ordering
        query = query.where(
            or_(
                model.created_at < params.created_at,
                and_(model.created_at == params.created_at, model.id > params.id),
            )
        )

    return query
