"""
Firebase implementation of User repository
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Try to import Firestore dependencies
    from google.cloud.firestore_v1 import FieldFilter

    FIRESTORE_AVAILABLE = True
    print("✅ Firestore imported successfully for User repository")
except ImportError as e:
    FIRESTORE_AVAILABLE = False
    print(f"⚠️ Firestore dependencies not available for User repository: {e}")

from app.domain.entities.user import SavedAddress, User, UserStatus
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.money import Money

if FIRESTORE_AVAILABLE:
    from ..converters import parse_datetime
    from .firebase_client import firebase_client


class FirebaseUserRepository(UserRepository):
    """Firebase implementation of User repository"""

    def __init__(self):
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("Firestore dependencies not available")
        if not firebase_client.is_available:
            raise RuntimeError("Firebase client not initialized")
        self.collection = firebase_client.collection("Users")

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        doc = self.collection.document(user_id).get()
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        query = self.collection.where("email", "==", email).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_phone(self, phone_number: str) -> Optional[User]:
        """Find user by phone number"""
        query = self.collection.where("phone_number", "==", phone_number).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_status_number(self, status_number: str) -> Optional[User]:
        """Find user by status number (ID/Passport)"""
        query = self.collection.where("status_number", "==", status_number).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
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
        # Build query with database-level filters
        query = self._build_query(status)

        # Execute query and get documents
        docs = list(query.stream())
        users = []

        # Process documents and apply client-side filters
        for doc in docs:
            try:
                user = self._to_entity(doc.id, doc.to_dict())
                if user and self._matches_filters(
                    user, verified_only, search, date_from, date_to
                ):
                    users.append(user)
            except Exception as e:
                print(f"Error processing user {doc.id}: {e}")
                continue

        # Apply pagination
        return self._paginate_results(users, page, limit)

    def _build_query(self, status: Optional[str]):
        """Build Firestore query with database-level filters"""
        query = self.collection

        # Apply simple filters at database level
        if status and status != "all":
            query = query.where("status", "==", status)

        # Fetch more than needed for client-side filtering
        query = query.limit(100)

        # Try to order by creation date
        try:
            query = query.order_by("created_at", direction="DESCENDING")
        except Exception:
            pass

        return query

    def _matches_filters(
        self,
        user: User,
        verified_only: Optional[bool],
        search: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> bool:
        """Check if user matches client-side filters"""
        if verified_only is not None:
            if verified_only and not user.is_verified:
                return False
            if not verified_only and user.is_verified:
                return False

        if date_from and user.created_at < date_from:
            return False

        if date_to and user.created_at > date_to:
            return False

        if search:
            search_lower = search.lower()
            if not (
                search_lower in user.email.lower()
                or search_lower in user.first_name.lower()
                or search_lower in user.last_name.lower()
                or search_lower in user.phone_number.lower()
                or search_lower in user.status_number.lower()
            ):
                return False

        return True

    def _paginate_results(self, users: List[User], page: int, limit: int) -> Dict[str, Any]:
        """Apply pagination to filtered users"""
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
        data = self._from_entity(user)

        if user.id and user.id != "new":
            # Update existing
            self.collection.document(user.id).set(data)
        else:
            # Create new
            doc_ref = self.collection.add(data)[1]
            user.id = doc_ref.id

        return user

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            self.collection.document(user_id).delete()
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count users by status"""
        query = self.collection.where("status", "==", status)
        return len(list(query.stream()))

    async def find_by_wallet_balance_above(self, amount: float) -> List[User]:
        """Find users with wallet balance above specified amount"""
        # Note: Firestore doesn't support complex number comparisons well
        # We'll fetch all users and filter client-side
        query = self.collection.limit(1000)  # Reasonable limit
        users = []

        for doc in query.stream():
            try:
                user = self._to_entity(doc.id, doc.to_dict())
                if user and user.wallet_balance.to_float() > amount:
                    users.append(user)
            except Exception:
                continue

        return users

    async def find_unverified_users(self, days_old: int = 7) -> List[User]:
        """Find users who haven't verified within specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        query = self.collection.where("status", "==", "pending_verification")

        users = []
        for doc in query.stream():
            try:
                user = self._to_entity(doc.id, doc.to_dict())
                if user and user.created_at <= cutoff_date:
                    users.append(user)
            except Exception:
                continue

        return users

    def _to_entity(self, doc_id: str, data: Dict[str, Any]) -> Optional[User]:
        """Convert Firestore document to User entity"""
        try:
            # Parse saved addresses
            saved_addresses = []
            addresses_data = data.get("saved_addresses", [])
            for addr_data in addresses_data:
                try:
                    address = SavedAddress(
                        id=addr_data.get("id"),
                        name=addr_data.get("name"),
                        address=addr_data.get("address"),
                        city=addr_data.get("city"),
                        coordinates=addr_data.get("coordinates"),
                        created_at=parse_datetime(addr_data.get("created_at", datetime.now())),
                    )
                    saved_addresses.append(address)
                except Exception as e:
                    print(f"Error parsing saved address: {e}")
                    continue

            # Parse wallet balance
            wallet_balance = Money(
                data.get("wallet_balance", 0),
                data.get("wallet_currency", "SAR")
            )

            # Create entity with defaults for missing data (backward compatibility)
            user = User(
                email=data.get("email", ""),
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone_number=data.get("phone_number", ""),
                nationality=data.get("nationality", ""),
                status_number=data.get("status_number", ""),
                status=(
                    UserStatus(data.get("status", "pending_verification"))
                    if data.get("status") in [s.value for s in UserStatus]
                    else UserStatus.PENDING_VERIFICATION
                ),
                wallet_balance=wallet_balance,
                preferred_language=data.get("preferred_language", "en"),
                email_verified=data.get("email_verified", False),
                phone_verified=data.get("phone_verified", False),
                saved_addresses=saved_addresses,
                user_data=data.get("user_data", {}),
            )

            # Set the document ID and timestamps manually after creation
            user.id = doc_id
            if data.get("created_at"):
                user.created_at = parse_datetime(data["created_at"])
            if data.get("updated_at"):
                user.updated_at = parse_datetime(data["updated_at"])

            return user

        except Exception as e:
            print(f"Error converting document to User entity: {e}")
            return None

    def _from_entity(self, user: User) -> Dict[str, Any]:
        """Convert User entity to Firestore document"""
        data = user.to_dict()

        # Convert datetime objects for Firestore
        data["created_at"] = user.created_at
        data["updated_at"] = user.updated_at

        # Convert saved addresses to simple dicts
        data["saved_addresses"] = [
            {
                "id": addr.id,
                "name": addr.name,
                "address": addr.address,
                "city": addr.city,
                "coordinates": addr.coordinates,
                "created_at": addr.created_at,
            }
            for addr in user.saved_addresses
        ]

        # Remove the id field as it's the document ID
        data.pop("id", None)
        # Remove computed fields
        data.pop("full_name", None)
        data.pop("is_verified", None)
        data.pop("can_make_bookings", None)

        return data