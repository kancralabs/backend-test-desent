"""Authentication endpoints - Level 5"""
from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.schemas.auth import TokenRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

# Demo user for Level 5 (hardcoded for simplicity)
# In production, this should be in database with proper user management
# Pre-computed bcrypt hash for password "secret123"
DEMO_USER = {
    "username": "admin",
    "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZQhXkFZi",  # Password: secret123
}


@router.post("/token", response_model=TokenResponse)
async def login(credentials: TokenRequest) -> TokenResponse:
    """
    Level 5: Generate JWT access token.

    Demo credentials:
    - Username: admin
    - Password: secret123

    Args:
        credentials: Username and password

    Returns:
        JWT access token

    Raises:
        HTTPException: 401 if credentials are incorrect
    """
    # Verify username
    if credentials.username != DEMO_USER["username"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, DEMO_USER["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": credentials.username}, expires_delta=access_token_expires
    )

    return TokenResponse(access_token=access_token, token_type="bearer")
