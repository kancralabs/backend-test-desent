"""Health check endpoints - Level 1 & 2"""
from typing import Any

from fastapi import APIRouter, Body

router = APIRouter(tags=["health"])


@router.get("/ping")
async def ping() -> dict[str, str]:
    """
    Level 1: Simple health check.

    Returns:
        {"message": "pong"}
    """
    return {"message": "pong"}


@router.post("/echo")
async def echo(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Level 2: Echo back request body without modification.

    Args:
        body: Any JSON object

    Returns:
        Same JSON object that was sent
    """
    return body
