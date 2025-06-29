"""
Car repository interface
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..entities.car import Car


class CarRepository(ABC):
    """Abstract repository for Car entity"""

    @abstractmethod
    async def find_by_id(self, car_id: str) -> Optional[Car]:
        """Find car by ID"""
        pass

    @abstractmethod
    async def find_by_license_plate(self, license_plate: str) -> Optional[Car]:
        """Find car by license plate"""
        pass

    @abstractmethod
    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        category: Optional[str] = None,
        make: Optional[str] = None,
        available_only: Optional[bool] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List cars with pagination and filters
        Returns dict with 'cars', 'total', 'page', 'total_pages'
        """
        pass

    @abstractmethod
    async def save(self, car: Car) -> Car:
        """Save or update car"""
        pass

    @abstractmethod
    async def delete(self, car_id: str) -> bool:
        """Delete car by ID"""
        pass

    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """Count cars by status"""
        pass

    @abstractmethod
    async def find_available_cars(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
    ) -> List[Car]:
        """Find all available cars"""
        pass

    @abstractmethod
    async def find_cars_due_for_service(self, days_ahead: int = 7) -> List[Car]:
        """Find cars due for service within specified days"""
        pass

    @abstractmethod
    async def find_cars_by_make_and_model(self, make: str, model: str) -> List[Car]:
        """Find cars by make and model"""
        pass
