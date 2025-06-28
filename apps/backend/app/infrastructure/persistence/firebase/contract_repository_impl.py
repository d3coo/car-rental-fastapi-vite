"""
Firebase implementation of Contract repository
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

try:
    # Try different import strategies to handle namespace conflicts
    import importlib
    import sys

    # Force reload of google namespace
    if "google" in sys.modules:
        importlib.reload(sys.modules["google"])

    # Try direct import
    from google.cloud.firestore_v1 import FieldFilter

    FIRESTORE_AVAILABLE = True
    print("✅ Firestore imported successfully")
except ImportError as e:
    try:
        # Alternative: try importing with modified path
        import sys

        original_path = sys.path[:]
        # Prioritize user packages
        user_packages = [p for p in sys.path if ".local" in p]
        system_packages = [p for p in sys.path if ".local" not in p]
        sys.path = user_packages + system_packages

        from google.cloud.firestore_v1 import FieldFilter

        FIRESTORE_AVAILABLE = True
        print("✅ Firestore imported successfully (with path adjustment)")
    except ImportError:
        sys.path = original_path
        FIRESTORE_AVAILABLE = False
        print(f"⚠️ Firestore dependencies not available - running in mock mode: {e}")
        print(
            "To fix: Create a virtual environment or resolve Google namespace conflicts"
        )

from app.domain.entities.contract import (
    Contract,
    ContractStatus,
    PaymentStatus,
    TransactionInfo,
)
from app.domain.repositories.contract_repository import ContractRepository
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.money import Money

if FIRESTORE_AVAILABLE:
    from ..converters import parse_datetime
    from .firebase_client import firebase_client


class FirebaseContractRepository(ContractRepository):
    """Firebase implementation of Contract repository"""

    def __init__(self):
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("Firestore dependencies not available")
        if not firebase_client.is_available:
            raise RuntimeError("Firebase client not initialized")
        self.collection = firebase_client.collection("Contracts")

    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        """Find contract by ID"""
        doc = self.collection.document(contract_id).get()
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_order_id(self, order_id: str) -> Optional[Contract]:
        """Find contract by order ID"""
        query = self.collection.where("OrderId", "==", order_id).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """Find contract by contract number"""
        query = self.collection.where("ContractNumber", "==", contract_number).limit(1)
        docs = query.stream()

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

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
        """List contracts with pagination and filters"""
        # Build query with database-level filters
        query = self._build_query(status)
        # Execute query and get documents
        docs = list(query.stream())
        contracts = []

        # Process documents and apply client-side filters
        for doc in docs:
            try:
                contract = self._to_entity(doc.id, doc.to_dict())
                if contract and self._matches_filters(
                    contract, payment_status, user_id, date_from, date_to, search
                ):
                    contracts.append(contract)
            except Exception as e:
                print(f"Error processing contract {doc.id}: {e}")
                continue

        # Apply pagination
        return self._paginate_results(contracts, page, limit)

    def _build_query(self, status: Optional[str]):
        """Build Firestore query with database-level filters"""
        query = self.collection

        # Apply simple filters at database level
        if status and status != "all":
            query = query.where("ContractStatus", "==", status)

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
        contract,
        payment_status: Optional[str],
        user_id: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        search: Optional[str],
    ) -> bool:
        """Check if contract matches client-side filters"""
        if payment_status and payment_status != "all":
            if contract.payment_status.value != payment_status:
                return False

        if user_id and contract.user_id != user_id:
            return False

        if date_from and contract.date_range.start_date < date_from:
            return False

        if date_to and contract.date_range.start_date > date_to:
            return False

        if search:
            search_lower = search.lower()
            if not (
                search_lower in contract.order_id.lower()
                or search_lower in contract.contract_number.lower()
                or search_lower in str(contract.booking_details).lower()
            ):
                return False

        return True

    def _paginate_results(self, contracts, page: int, limit: int) -> Dict[str, Any]:
        """Apply pagination to filtered contracts"""
        total = len(contracts)
        offset = (page - 1) * limit
        paginated_contracts = contracts[offset : offset + limit]

        return {
            "contracts": [c.to_dict() for c in paginated_contracts],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit,
            "hasMore": page < (total + limit - 1) // limit,
        }

    async def save(self, contract: Contract) -> Contract:
        """Save or update contract"""
        data = self._from_entity(contract)

        if contract.id and contract.id != "new":
            # Update existing
            self.collection.document(contract.id).set(data)
        else:
            # Create new
            doc_ref = self.collection.add(data)[1]
            contract.id = doc_ref.id

        return contract

    async def delete(self, contract_id: str) -> bool:
        """Delete contract by ID"""
        try:
            self.collection.document(contract_id).delete()
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count contracts by status"""
        query = self.collection.where("ContractStatus", "==", status)
        return len(list(query.stream()))

    async def find_overdue(self) -> List[Contract]:
        """Find all overdue contracts"""
        query = self.collection.where(
            filter=FieldFilter("ContractStatus", "in", ["active", "extended"])
        )

        contracts = []
        for doc in query.stream():
            try:
                contract = self._to_entity(doc.id, doc.to_dict())
                if contract and contract.is_overdue():
                    contracts.append(contract)
            except Exception:
                continue

        return contracts

    async def find_expiring_soon(self, days: int = 7) -> List[Contract]:
        """Find contracts expiring within specified days"""
        future_date = datetime.now() + timedelta(days=days)
        query = self.collection.where(
            filter=FieldFilter("ContractStatus", "in", ["active", "extended"])
        )

        contracts = []
        for doc in query.stream():
            try:
                contract = self._to_entity(doc.id, doc.to_dict())
                if contract and contract.date_range.end_date <= future_date:
                    contracts.append(contract)
            except Exception:
                continue

        return contracts

    def _normalize_booking_type(self, booking_type_raw: Any) -> str:
        """Normalize booking type from various formats"""
        if not booking_type_raw:
            return "Day"

        booking_type = str(booking_type_raw).strip()
        # Handle common variations
        if booking_type.lower() in ["day", "days", "daily"]:
            return "Day"
        elif booking_type.lower() in ["week", "weeks", "weekly"]:
            return "Week"
        elif booking_type.lower() in ["month", "months", "monthly"]:
            return "Month"
        else:
            # Default to Day for unknown types
            return "Day"

    def _to_entity(self, doc_id: str, data: Dict[str, Any]) -> Optional[Contract]:
        """Convert Firestore document to Contract entity"""
        try:
            # Parse dates
            start_date = parse_datetime(data.get("start_date"))
            end_date = parse_datetime(data.get("end_date"))

            # Parse money values
            booking_cost = Money(
                data.get("booking_cost", 0), data.get("Currency", "SAR")
            )
            taxes = Money(data.get("taxes", 0), data.get("Currency", "SAR"))
            delivery = Money(data.get("Delivery", 0), data.get("Currency", "SAR"))
            offers_total = Money(
                data.get("offersTotal", 0), data.get("Currency", "SAR")
            )
            total_cost = Money(data.get("total_cost", 0), data.get("Currency", "SAR"))

            # Parse transaction info
            transaction_info = None
            trans_data = data.get("transaction_info") or data.get("tansaction_info")
            if trans_data:
                trans_status = trans_data.get("status", "pending")
                transaction_info = TransactionInfo(
                    status=(
                        PaymentStatus(trans_status)
                        if trans_status in [s.value for s in PaymentStatus]
                        else PaymentStatus.PENDING
                    ),
                    transaction_id=trans_data.get("transaction_id"),
                    payment_method=trans_data.get("type"),
                )

            # Create entity with defaults for missing data (backward compatibility)
            contract = Contract(
                order_id=data.get(
                    "OrderId", data.get("order_id", f"ORDER_{doc_id[:8]}")
                ),
                contract_number=data.get(
                    "ContractNumber", data.get("contract_number", f"CNT_{doc_id[:8]}")
                ),
                user_id=data.get(
                    "user_id", data.get("User", data.get("userId", "unknown_user"))
                ),
                car_id=data.get(
                    "car_id", data.get("Car", data.get("carId", "unknown_car"))
                ),
                booking_id=data.get("booking_id"),
                date_range=DateRange(start_date, end_date),
                booking_type=self._normalize_booking_type(
                    data.get("BookingDetails", {}).get("BookingType")
                    or data.get("BookingType")
                ),
                count=data.get("count", 1),
                booking_cost=booking_cost,
                taxes=taxes,
                delivery_fee=delivery,
                offers_total=offers_total,
                total_cost=total_cost,
                status=(
                    ContractStatus(data.get("ContractStatus", "active"))
                    if data.get("ContractStatus") in [s.value for s in ContractStatus]
                    else ContractStatus.ACTIVE
                ),
                payment_status=(
                    PaymentStatus(trans_data.get("status", "pending"))
                    if trans_data
                    and trans_data.get("status") in [s.value for s in PaymentStatus]
                    else PaymentStatus.PENDING
                ),
                transaction_info=transaction_info,
                is_extended=data.get("IsExtended", False),
                booking_details=data.get("BookingDetails", {}),
            )

            # Set the document ID and timestamps manually after creation
            contract.id = doc_id
            if data.get("created_at"):
                contract.created_at = parse_datetime(data["created_at"])
            if data.get("updated_at"):
                contract.updated_at = parse_datetime(data["updated_at"])

            return contract

        except Exception as e:
            print(f"Error converting document to Contract entity: {e}")
            return None

    def _from_entity(self, contract: Contract) -> Dict[str, Any]:
        """Convert Contract entity to Firestore document"""
        data = contract.to_dict()

        # Convert datetime objects for Firestore
        data["start_date"] = contract.date_range.start_date
        data["end_date"] = contract.date_range.end_date
        data["created_at"] = contract.created_at
        data["updated_at"] = contract.updated_at

        # Remove the id field as it's the document ID
        data.pop("id", None)

        return data
