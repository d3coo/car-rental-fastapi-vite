"""
Cars API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.domain.repositories.car_repository import CarRepository
from app.infrastructure.dependencies import get_car_repository

router = APIRouter(prefix="/cars", tags=["cars"])


class CarResponse(BaseModel):
    """Car response model"""

    id: str
    make: str
    model: str
    year: int
    color: str
    license_plate: str
    category: str
    display_name: str
    age_years: int
    is_new: bool
    daily_rate: float
    weekly_rate: Optional[float]
    monthly_rate: Optional[float]
    currency: str
    status: str
    is_available: bool
    location: Optional[str]
    mileage: Optional[int]
    fuel_type: Optional[str]
    transmission: Optional[str]
    seats: Optional[int]
    features: list
    created_at: str
    updated_at: str


class CarCreate(BaseModel):
    """Car creation model"""

    make: str
    model: str
    year: int
    color: str
    license_plate: str
    category: str
    daily_rate: float


@router.get("/")
async def get_cars(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    make: Optional[str] = Query(None),
    available_only: Optional[bool] = Query(None),
    location: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    repository: CarRepository = Depends(get_car_repository),
):
    """Get all cars with pagination and filters"""
    try:
        result = await repository.list(
            page=page,
            limit=limit,
            status=status,
            category=category,
            make=make,
            available_only=available_only,
            location=location,
            search=search,
        )
        return {
            "data": result,
            "message": "Cars retrieved successfully",
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cars: {str(e)}",
        )


@router.get("/available")
async def get_available_cars(
    category: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    repository: CarRepository = Depends(get_car_repository),
):
    """Get all available cars"""
    try:
        cars = await repository.find_available_cars(
            category=category,
            location=location,
        )
        return {
            "data": {"cars": [c.to_dict() for c in cars]},
            "message": "Available cars retrieved successfully",
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve available cars: {str(e)}",
        )


@router.get("/due-for-service")
async def get_cars_due_for_service(
    days_ahead: int = Query(7, ge=1, le=30),
    repository: CarRepository = Depends(get_car_repository),
):
    """Get cars due for service"""
    try:
        cars = await repository.find_cars_due_for_service(days_ahead=days_ahead)
        return {
            "data": {"cars": [c.to_dict() for c in cars]},
            "message": f"Cars due for service in {days_ahead} days retrieved successfully",
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve cars due for service: {str(e)}",
        )


@router.get("/{car_id}")
async def get_car(
    car_id: str, repository: CarRepository = Depends(get_car_repository)
):
    """Get car by ID"""
    try:
        car = await repository.find_by_id(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        return {
            "data": car.to_dict(),
            "message": "Car retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve car: {str(e)}",
        )


@router.get("/license/{license_plate}")
async def get_car_by_license_plate(
    license_plate: str, repository: CarRepository = Depends(get_car_repository)
):
    """Get car by license plate"""
    try:
        car = await repository.find_by_license_plate(license_plate)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        return {
            "data": car.to_dict(),
            "message": "Car retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve car: {str(e)}",
        )


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
async def create_car(car: CarCreate):
    """Create new car"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.put("/{car_id}", response_model=CarResponse)
async def update_car(car_id: str, car: CarCreate):
    """Update car"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: str):
    """Delete car"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.post("/{car_id}/mark-rented")
async def mark_car_as_rented(
    car_id: str, repository: CarRepository = Depends(get_car_repository)
):
    """Mark car as rented"""
    try:
        car = await repository.find_by_id(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        car.mark_as_rented()
        await repository.save(car)

        return {
            "data": car.to_dict(),
            "message": "Car marked as rented successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark car as rented: {str(e)}",
        )


@router.post("/{car_id}/mark-available")
async def mark_car_as_available(
    car_id: str, repository: CarRepository = Depends(get_car_repository)
):
    """Mark car as available"""
    try:
        car = await repository.find_by_id(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        car.mark_as_available()
        await repository.save(car)

        return {
            "data": car.to_dict(),
            "message": "Car marked as available successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark car as available: {str(e)}",
        )


@router.post("/{car_id}/maintenance")
async def send_car_for_maintenance(
    car_id: str,
    reason: Optional[str] = Query(None),
    repository: CarRepository = Depends(get_car_repository),
):
    """Send car for maintenance"""
    try:
        car = await repository.find_by_id(car_id)
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Car not found"
            )

        car.send_for_maintenance(reason)
        await repository.save(car)

        return {
            "data": car.to_dict(),
            "message": "Car sent for maintenance successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send car for maintenance: {str(e)}",
        )