"""User endpoints"""
from fastapi import APIRouter, Depends, status

from app.dependencies import get_user_service
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Register a new user.

    - **username**: unique, 3-50 characters
    - **email**: unique, valid email format
    - **password**: minimum 6 characters
    """
    return await service.create_user(data)
