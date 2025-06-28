"""
Contracts API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.domain.repositories.contract_repository import ContractRepository
from app.infrastructure.dependencies import get_contract_repository

router = APIRouter(prefix="/contracts", tags=["contracts"])


class ContractResponse(BaseModel):
    """Contract response model"""

    id: str
    OrderId: str
    ContractNumber: str
    user_id: str
    car_id: str
    booking_id: Optional[str] = None
    start_date: str
    end_date: str
    count: int
    BookingType: str
    booking_cost: float
    taxes: float
    Delivery: float
    offersTotal: float
    total_cost: float
    Currency: str
    ContractStatus: str
    payment_status: str
    IsExtended: bool
    created_at: str
    updated_at: str


class ContractCreate(BaseModel):
    """Contract creation model"""

    user_id: str
    car_id: str
    start_date: str
    end_date: str


@router.get("/")
async def get_contracts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    repository: ContractRepository = Depends(get_contract_repository),
):
    """Get all contracts with pagination and filters"""
    try:
        result = await repository.list(
            page=page,
            limit=limit,
            status=status,
            payment_status=payment_status,
            user_id=user_id,
            search=search,
        )
        return {
            "data": result,
            "message": "Contracts retrieved successfully",
            "status_code": 200,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contracts: {str(e)}",
        )


@router.get("/{contract_id}")
async def get_contract(
    contract_id: str, repository: ContractRepository = Depends(get_contract_repository)
):
    """Get contract by ID"""
    try:
        contract = await repository.find_by_id(contract_id)
        if not contract:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
            )

        return {
            "data": contract.to_dict(),
            "message": "Contract retrieved successfully",
            "status_code": 200,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve contract: {str(e)}",
        )


@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(contract: ContractCreate):
    """Create new contract"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.put("/{contract_id}", response_model=ContractResponse)
async def update_contract(contract_id: str, contract: ContractCreate):
    """Update contract"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )


@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(contract_id: str):
    """Delete contract"""
    # TODO: Implement with actual use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet"
    )
