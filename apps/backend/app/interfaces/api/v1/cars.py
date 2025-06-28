"""
Cars API endpoints
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/cars", tags=["cars"])


class CarResponse(BaseModel):
    """Car response model"""
    id: str
    make: str
    model: str
    year: int
    available: bool


@router.get("/", response_model=List[CarResponse])
async def get_cars():
    """Get all cars"""
    # TODO: Implement with actual repository
    return []


@router.get("/available", response_model=List[CarResponse])
async def get_available_cars():
    """Get available cars"""
    # TODO: Implement with actual repository
    return []