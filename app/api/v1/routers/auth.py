"""Authentication endpoints"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import settings
from app.core.security import create_access_token, verify_password
from app.dependencies import get_user_repository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=TokenResponse)
async def login(
    credentials: TokenRequest,
    user_repo: UserRepository = Depends(get_user_repository),
) -> TokenResponse:
    """
    Generate JWT access token.

    Args:
        credentials: Username and password

    Returns:
        JWT access token

    Raises:
        HTTPException: 401 if credentials are incorrect
    """
    user = await user_repo.get_by_username(credentials.username)

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return TokenResponse(access_token=access_token, token_type="bearer")
