"""
Users API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.dependencies import get_user_repository

router = APIRouter(prefix="/users", tags=["users"])


class UserResponse(BaseModel):
    """User response model"""

    id: str
    email: str
    first_name: str
    last_name: str
    full_name: str
    phone_number: str
    nationality: str
    status_number: str
    status: str
    wallet_balance: float
    wallet_currency: str
    preferred_language: str
    email_verified: bool
    phone_verified: bool
    is_verified: bool
    can_make_bookings: bool
    created_at: str
    updated_at: str


class UserCreate(BaseModel):
    """User creation model"""

    email: str
    first_name: str
    last_name: str
    phone_number: str
    nationality: str
    status_number: str


@router.get("/")
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    verified_only: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    repository: UserRepository = Depends(get_user_repository),
):
    """Get all users with pagination and filters"""
    try:
        result = await repository.list(
            page=page,
            limit=limit,
            status=status,
            verified_only=verified_only,
            search=search,
        )
        return {
            "data": result,
            "message": "Users retrieved successfully",
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}",
        )


@router.get("/{user_id}")
async def get_user(
    user_id: str, repository: UserRepository = Depends(get_user_repository)
):
    """Get user by ID"""
    try:
        user = await repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "data": user.to_dict(),
            "message": "User retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}",
        )


@router.get("/email/{email}")
async def get_user_by_email(
    email: str, repository: UserRepository = Depends(get_user_repository)
):
    """Get user by email"""
    try:
        user = await repository.find_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "data": user.to_dict(),
            "message": "User retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}",
        )


@router.get("/phone/{phone}")
async def get_user_by_phone(
    phone: str, repository: UserRepository = Depends(get_user_repository)
):
    """Get user by phone number"""
    try:
        user = await repository.find_by_phone(phone)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return {
            "data": user.to_dict(),
            "message": "User retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user: {str(e)}",
        )


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """Create new user"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate):
    """Update user"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    """Delete user"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.post("/{user_id}/verify-email")
async def verify_email(
    user_id: str, repository: UserRepository = Depends(get_user_repository)
):
    """Verify user's email"""
    try:
        user = await repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.verify_email()
        await repository.save(user)

        return {
            "data": user.to_dict(),
            "message": "Email verified successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify email: {str(e)}",
        )


@router.post("/{user_id}/verify-phone")
async def verify_phone(
    user_id: str, repository: UserRepository = Depends(get_user_repository)
):
    """Verify user's phone"""
    try:
        user = await repository.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user.verify_phone()
        await repository.save(user)

        return {
            "data": user.to_dict(),
            "message": "Phone verified successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify phone: {str(e)}",
        )
