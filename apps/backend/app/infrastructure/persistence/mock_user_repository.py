"""
Mock implementation of User repository for testing and fallback
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.domain.entities.user import SavedAddress, User, UserStatus
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.money import Money


class MockUserRepository(UserRepository):
    """Mock implementation of User repository"""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._create_sample_data()

    def _create_sample_data(self):
        """Create sample users for testing"""
        # Create sample users
        sample_users = [
            {
                "email": "john.doe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "phone_number": "+966501234567",
                "nationality": "Saudi",
                "status_number": "1234567890",
                "status": UserStatus.ACTIVE,
                "wallet_balance": Money(1500, "SAR"),
                "email_verified": True,
                "phone_verified": True,
            },
            {
                "email": "jane.smith@example.com",
                "first_name": "Jane",
                "last_name": "Smith",
                "phone_number": "+966509876543",
                "nationality": "American",
                "status_number": "0987654321",
                "status": UserStatus.PENDING_VERIFICATION,
                "wallet_balance": Money(0, "SAR"),
                "email_verified": False,
                "phone_verified": False,
            },
            {
                "email": "ahmed.ali@example.com",
                "first_name": "Ahmed",
                "last_name": "Ali",
                "phone_number": "+966555123456",
                "nationality": "Saudi",
                "status_number": "5555555555",
                "status": UserStatus.ACTIVE,
                "wallet_balance": Money(750, "SAR"),
                "email_verified": True,
                "phone_verified": True,
            },
        ]

        for user_data in sample_users:
            user = User(**user_data)
            # Set ID manually after creation to avoid constructor issues
            user.id = f"user_{len(self._users) + 1}"
            
            # Add sample saved address for first user
            if user.email == "john.doe@example.com":
                address = SavedAddress(
                    id=str(uuid.uuid4()),
                    name="Home",
                    address="123 Main St, Riyadh",
                    city="Riyadh",
                    coordinates={"lat": 24.7136, "lng": 46.6753},
                )
                user.saved_addresses.append(address)
            
            self._users[user.id] = user

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        for user in self._users.values():
            if user.email.lower() == email.lower():
                return user
        return None

    async def find_by_phone(self, phone_number: str) -> Optional[User]:
        """Find user by phone number"""
        for user in self._users.values():
            if user.phone_number == phone_number:
                return user
        return None

    async def find_by_status_number(self, status_number: str) -> Optional[User]:
        """Find user by status number (ID/Passport)"""
        for user in self._users.values():
            if user.status_number == status_number:
                return user
        return None

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
        """List users with pagination and filters"""
        users = list(self._users.values())

        # Apply filters
        if status and status != "all":
            users = [u for u in users if u.status.value == status]

        if verified_only is not None:
            if verified_only:
                users = [u for u in users if u.is_verified]
            else:
                users = [u for u in users if not u.is_verified]

        if search:
            search_lower = search.lower()
            users = [
                u
                for u in users
                if (
                    search_lower in u.email.lower()
                    or search_lower in u.first_name.lower()
                    or search_lower in u.last_name.lower()
                    or search_lower in u.phone_number.lower()
                    or search_lower in u.status_number.lower()
                )
            ]

        if date_from:
            users = [u for u in users if u.created_at >= date_from]

        if date_to:
            users = [u for u in users if u.created_at <= date_to]

        # Sort by creation date (newest first)
        users.sort(key=lambda x: x.created_at, reverse=True)

        # Apply pagination
        total = len(users)
        offset = (page - 1) * limit
        paginated_users = users[offset : offset + limit]

        return {
            "users": [u.to_dict() for u in paginated_users],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit,
            "hasMore": page < (total + limit - 1) // limit,
        }

    async def save(self, user: User) -> User:
        """Save or update user"""
        if not user.id or user.id == "new":
            user.id = f"user_{len(self._users) + 1}"

        user.mark_updated()
        self._users[user.id] = user
        return user

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False

    async def count_by_status(self, status: str) -> int:
        """Count users by status"""
        return len([u for u in self._users.values() if u.status.value == status])

    async def find_by_wallet_balance_above(self, amount: float) -> List[User]:
        """Find users with wallet balance above specified amount"""
        return [
            u for u in self._users.values() if u.wallet_balance.to_float() > amount
        ]

    async def find_unverified_users(self, days_old: int = 7) -> List[User]:
        """Find users who haven't verified within specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        return [
            u
            for u in self._users.values()
            if u.status == UserStatus.PENDING_VERIFICATION and u.created_at <= cutoff_date
        ]