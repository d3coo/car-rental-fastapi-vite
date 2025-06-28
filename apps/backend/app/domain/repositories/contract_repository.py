"""
Contract repository interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..entities.contract import Contract


class ContractRepository(ABC):
    """Abstract repository for Contract entity"""

    @abstractmethod
    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        """Find contract by ID"""
        pass

    @abstractmethod
    async def find_by_order_id(self, order_id: str) -> Optional[Contract]:
        """Find contract by order ID"""
        pass

    @abstractmethod
    async def find_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """Find contract by contract number"""
        pass

    @abstractmethod
    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        payment_status: Optional[str] = None,
        user_id: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List contracts with pagination and filters
        Returns dict with 'contracts', 'total', 'page', 'total_pages'
        """
        pass

    @abstractmethod
    async def save(self, contract: Contract) -> Contract:
        """Save or update contract"""
        pass

    @abstractmethod
    async def delete(self, contract_id: str) -> bool:
        """Delete contract by ID"""
        pass

    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """Count contracts by status"""
        pass

    @abstractmethod
    async def find_overdue(self) -> List[Contract]:
        """Find all overdue contracts"""
        pass

    @abstractmethod
    async def find_expiring_soon(self, days: int = 7) -> List[Contract]:
        """Find contracts expiring within specified days"""
        pass
