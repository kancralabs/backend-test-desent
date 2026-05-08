"""Dependency injection setup for FastAPI"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.book_repository import BookRepository
from app.repositories.user_repository import UserRepository
from app.services.book_service import BookService
from app.services.user_service import UserService


def get_book_repository(db: AsyncSession = Depends(get_db)) -> BookRepository:
    return BookRepository(db)


def get_book_service(repository: BookRepository = Depends(get_book_repository)) -> BookService:
    return BookService(repository)


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repository)
