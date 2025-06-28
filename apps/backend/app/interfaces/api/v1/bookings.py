"""
Bookings API endpoints
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/bookings", tags=["bookings"])


class BookingResponse(BaseModel):
    """Booking response model"""
    id: str
    user_id: str
    car_id: str
    status: str
    start_date: str
    end_date: str


@router.get("/", response_model=List[BookingResponse])
async def get_bookings():
    """Get all bookings"""
    # TODO: Implement with actual repository
    return []


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: str):
    """Get booking by ID"""
    # TODO: Implement with actual repository
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Booking not found"
    )