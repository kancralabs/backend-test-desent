"""Pydantic schemas for Book request/response"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BookBase(BaseModel):
    """Base book fields shared across schemas"""

    title: str = Field(..., min_length=1, max_length=500, description="Book title")
    author: str = Field(..., min_length=1, max_length=200, description="Book author")
    published_year: Optional[int] = Field(None, ge=1000, le=2100, description="Publication year")


class BookCreate(BookBase):
    """Schema for creating a book (POST /books)"""

    pass


class BookUpdate(BaseModel):
    """Schema for updating a book (PUT /books/{id})"""

    title: Optional[str] = Field(None, min_length=1, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=200)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)


class BookResponse(BookBase):
    """Schema for book response (GET /books, GET /books/{id})"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    # Pydantic v2: Enable ORM mode for SQLAlchemy model conversion
    model_config = ConfigDict(from_attributes=True)
