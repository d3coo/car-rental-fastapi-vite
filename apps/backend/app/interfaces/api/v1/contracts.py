"""
Contracts API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/contracts", tags=["contracts"])


class ContractResponse(BaseModel):
    """Contract response model"""

    id: str
    user_id: str
    car_id: str
    status: str
    start_date: str
    end_date: str
    total_amount: float


class ContractCreate(BaseModel):
    """Contract creation model"""

    user_id: str
    car_id: str
    start_date: str
    end_date: str


@router.get("/", response_model=List[ContractResponse])
async def get_contracts(skip: int = 0, limit: int = 100):
    """Get all contracts"""
    # TODO: Implement with actual repository
    return []


@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract(contract_id: str):
    """Get contract by ID"""
    # TODO: Implement with actual repository
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
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
