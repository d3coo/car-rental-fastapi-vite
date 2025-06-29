"""
User repository interface
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..entities.user import User


class UserRepository(ABC):
    """Abstract repository for User entity"""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        pass

    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    @abstractmethod
    async def find_by_phone(self, phone_number: str) -> Optional[User]:
        """Find user by phone number"""
        pass

    @abstractmethod
    async def find_by_status_number(self, status_number: str) -> Optional[User]:
        """Find user by status number (ID/Passport)"""
        pass

    @abstractmethod
    async def list(
        self,
        page: int = 1,
        limit: int = 20,
        status: Optional[str] = None,
        verified_only: Optional[bool] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        List users with pagination and filters
        Returns dict with 'users', 'total', 'page', 'total_pages'
        """
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save or update user"""
        pass

    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    async def count_by_status(self, status: str) -> int:
        """Count users by status"""
        pass

    @abstractmethod
    async def find_by_wallet_balance_above(self, amount: float) -> List[User]:
        """Find users with wallet balance above specified amount"""
        pass

    @abstractmethod
    async def find_unverified_users(self, days_old: int = 7) -> List[User]:
        """Find users who haven't verified within specified days"""
        pass
