"""User service - Business logic layer"""
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate) -> UserResponse:
        if await self.repository.get_by_username(data.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{data.username}' is already taken",
            )

        if await self.repository.get_by_email(data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{data.email}' is already registered",
            )

        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        created = await self.repository.create(user)
        return UserResponse.model_validate(created)
