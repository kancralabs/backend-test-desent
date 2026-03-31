"""Dependency injection setup for FastAPI"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.book_repository import BookRepository
from app.services.book_service import BookService


def get_book_repository(db: AsyncSession = Depends(get_db)) -> BookRepository:
    """
    Dependency for injecting BookRepository.

    Usage:
        @router.get("/")
        async def list_books(repo: BookRepository = Depends(get_book_repository)):
            return await repo.list_paginated()
    """
    return BookRepository(db)


def get_book_service(repository: BookRepository = Depends(get_book_repository)) -> BookService:
    """
    Dependency for injecting BookService.

    Usage:
        @router.get("/")
        async def list_books(service: BookService = Depends(get_book_service)):
            return await service.list_books()
    """
    return BookService(repository)
