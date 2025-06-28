"""
Users API endpoints
"""

from typing import List

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    """User response model"""

    id: str
    email: str
    name: str


@router.get("/", response_model=List[UserResponse])
async def get_users():
    """Get all users"""
    # TODO: Implement with actual repository
    return []
