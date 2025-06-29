"""
Firebase implementation of User repository
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Try to import Firestore dependencies
    FIRESTORE_AVAILABLE = True
    print("✅ Firestore imported successfully for User repository")
except ImportError as e:
    FIRESTORE_AVAILABLE = False
    print(f"⚠️ Firestore dependencies not available for User repository: {e}")

from app.domain.entities.user import User, UserStatus
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
        self.collection = firebase_client.collection(
            "users"
        )  # Firebase collection is lowercase
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def _run_query(self, query):
        """Helper to run Firestore query asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: list(query.stream()))

    async def _get_document(self, doc_ref):
        """Helper to get Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, doc_ref.get)

    async def _set_document(self, doc_ref, data):
        """Helper to set Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: doc_ref.set(data))

    async def _add_document(self, data):
        """Helper to add Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, lambda: self.collection.add(data)
        )

    async def _delete_document(self, doc_ref):
        """Helper to delete Firestore document asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, doc_ref.delete)

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        doc = await self._get_document(self.collection.document(user_id))
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        query = self.collection.where("email", "==", email).limit(1)
        docs = await self._run_query(query)

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_phone(self, phone_number: str) -> Optional[User]:
        """Find user by phone number"""
        query = self.collection.where("phone_number", "==", phone_number).limit(1)
        docs = await self._run_query(query)

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_status_number(self, status_number: str) -> Optional[User]:
        """Find user by status number (ID/Passport)"""
        query = self.collection.where("status_number", "==", status_number).limit(1)
        docs = await self._run_query(query)

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
        # Start with basic query - Firebase doesn't have DDD status field
        query = self.collection.limit(
            100
        )  # Get reasonable amount for client-side filtering

        # Execute query and get documents
        docs = await self._run_query(query)
        users = []

        # Process documents and apply client-side filters
        for doc in docs:
            try:
                user = self._to_entity(doc.id, doc.to_dict())
                if user and self._matches_all_filters(
                    user, status, verified_only, search, date_from, date_to
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

    def _matches_all_filters(
        self,
        user: User,
        status: Optional[str] = None,
        verified_only: Optional[bool] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> bool:
        """Check if user matches all client-side filters"""
        # Status filter
        if status and status != "all":
            if user.status.value != status:
                return False

        # Verified only filter
        if verified_only is not None:
            if verified_only and not user.is_verified:
                return False
            if not verified_only and user.is_verified:
                return False

        # Date range filters
        if date_from and user.created_at < date_from:
            return False

        if date_to and user.created_at > date_to:
            return False

        # Search filter
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

    def _paginate_results(
        self, users: List[User], page: int, limit: int
    ) -> Dict[str, Any]:
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
            await self._set_document(self.collection.document(user.id), data)
        else:
            # Create new
            _, doc_ref = await self._add_document(data)
            user.id = doc_ref.id

        return user

    async def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        try:
            await self._delete_document(self.collection.document(user_id))
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count users by status"""
        query = self.collection.where("status", "==", status)
        docs = await self._run_query(query)
        return len(docs)

    async def find_by_wallet_balance_above(self, amount: float) -> List[User]:
        """Find users with wallet balance above specified amount"""
        # Note: Firestore doesn't support complex number comparisons well
        # We'll fetch all users and filter client-side
        query = self.collection.limit(1000)  # Reasonable limit
        users = []

        docs = await self._run_query(query)
        for doc in docs:
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
        docs = await self._run_query(query)
        for doc in docs:
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
            # Clean Firebase objects first
            cleaned_data = self._clean_firebase_objects(data)

            # EXACT Firebase field mapping based on MCP schema:
            # uid: document ID
            # email: user email
            # First_name: first name (capital F)
            # Last_name: last name (capital L)
            # phone_number: phone number
            # Nationality: nationality
            # StatusNumer: status number (Firebase typo: missing 'b')
            # Wallet_Balance: wallet balance
            # Status: "Citizen", "Resident", etc.
            # Currency: "SAR"
            # created_time: timestamp

            # Parse saved addresses (Firebase schema doesn't include this)
            saved_addresses = []

            # Parse wallet balance using exact Firebase field
            wallet_balance = Money(
                cleaned_data.get("Wallet_Balance", 0),
                cleaned_data.get("Currency", "SAR"),
            )

            # Map user status using exact Firebase values
            status_str = cleaned_data.get("Status", "pending_verification").lower()
            status_mapping = {
                "citizen": UserStatus.ACTIVE,
                "resident": UserStatus.ACTIVE,
                "visitor": UserStatus.PENDING_VERIFICATION,
            }
            status = status_mapping.get(status_str, UserStatus.PENDING_VERIFICATION)

            # Create entity using EXACT Firebase schema
            user = User(
                email=cleaned_data.get("email", ""),
                first_name=cleaned_data.get(
                    "First_name", ""
                ),  # EXACT: "First_name" (capital F)
                last_name=cleaned_data.get(
                    "Last_name", ""
                ),  # EXACT: "Last_name" (capital L)
                phone_number=str(
                    cleaned_data.get("phone_number", "")
                ),  # EXACT: "phone_number"
                nationality=cleaned_data.get(
                    "Nationality", ""
                ),  # EXACT: "Nationality" (capital N)
                status_number=cleaned_data.get(
                    "StatusNumer", ""
                ),  # EXACT: "StatusNumer" (Firebase typo)
                status=status,
                wallet_balance=wallet_balance,
                preferred_language="ar",  # Inferred from Arabic names in Firebase
                email_verified=bool(
                    cleaned_data.get("email")
                ),  # Inferred: has email = verified
                phone_verified=bool(
                    cleaned_data.get("phone_number")
                ),  # Inferred: has phone = verified
                saved_addresses=saved_addresses,  # Firebase schema doesn't include this
                user_data={
                    "uid": cleaned_data.get("uid"),
                    "display_name": cleaned_data.get("display_name"),
                    "photo_url": cleaned_data.get("photo_url"),
                    "regPlatform": cleaned_data.get("regPlatform"),
                },
            )

            # Set the document ID and timestamps using exact Firebase schema
            user.id = doc_id
            # EXACT Firebase field: "created_time" (Timestamp)
            if cleaned_data.get("created_time"):
                user.created_at = parse_datetime(cleaned_data["created_time"])
            else:
                user.created_at = datetime.now()
            user.updated_at = (
                datetime.now()
            )  # Firebase schema doesn't include updated_at

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

    def _clean_firebase_objects(self, obj: Any) -> Any:
        """Clean Firebase objects for JSON serialization"""
        try:
            # Import here to avoid circular dependencies
            from google.cloud.firestore_v1._helpers import (
                DatetimeWithNanoseconds,
                GeoPoint,
            )
            from google.cloud.firestore_v1.document import DocumentReference

            if isinstance(obj, DocumentReference):
                # Extract just the document ID from the reference
                return obj.id
            elif isinstance(obj, DatetimeWithNanoseconds):
                # Convert to ISO string
                return obj.isoformat()
            elif isinstance(obj, GeoPoint):
                # Convert to lat/lng dict
                return {"lat": obj.latitude, "lng": obj.longitude}
            elif isinstance(obj, dict):
                # Recursively clean dictionaries
                return {k: self._clean_firebase_objects(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                # Recursively clean lists
                return [self._clean_firebase_objects(item) for item in obj]
            else:
                # Return primitive types as-is
                return obj
        except Exception as e:
            print(f"Warning: Error cleaning Firebase object: {e}")
            return str(obj)  # Fallback to string representation
