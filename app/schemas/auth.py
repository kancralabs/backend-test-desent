"""Pydantic schemas for authentication"""
from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """Schema for login request (POST /auth/token)"""

    username: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password")


class TokenResponse(BaseModel):
    """Schema for JWT token response"""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")
