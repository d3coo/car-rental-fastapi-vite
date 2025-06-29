"""
Firebase implementation of Contract repository
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
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
    from google.cloud import firestore
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

        from google.cloud import firestore
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
        self.collection = firebase_client.collection(
            "Contracts"
        )  # EXACT Firebase collection name
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

    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        """Find contract by ID"""
        doc = await self._get_document(self.collection.document(contract_id))
        if doc.exists:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_order_id(self, order_id: str) -> Optional[Contract]:
        """Find contract by order ID"""
        query = self.collection.where("OrderId", "==", order_id).limit(1)
        docs = await self._run_query(query)

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def find_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """Find contract by contract number"""
        query = self.collection.where("ContractNumber", "==", contract_number).limit(1)
        docs = await self._run_query(query)

        for doc in docs:
            return self._to_entity(doc.id, doc.to_dict())
        return None

    async def list(  # noqa: C901 - Complex but necessary for comprehensive filtering
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
        query = self.collection

        # Apply simple filters at database level
        if status and status != "all":
            query = query.where("ContractStatus", "==", status)

        # Fetch more than needed for client-side filtering
        query = query.limit(100)

        # Try to order by creation date
        try:
            query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
        except Exception:
            pass

        # Execute query
        docs = await self._run_query(query)
        contracts = []

        for doc in docs:
            try:
                contract = self._to_entity(doc.id, doc.to_dict())
                if contract:
                    # Apply client-side filters
                    include = True

                    if payment_status and payment_status != "all":
                        include = (
                            include and contract.payment_status.value == payment_status
                        )

                    if user_id:
                        include = include and contract.user_id == user_id

                    if date_from:
                        include = (
                            include and contract.date_range.start_date >= date_from
                        )

                    if date_to:
                        include = include and contract.date_range.start_date <= date_to

                    if search:
                        search_lower = search.lower()
                        include = include and (
                            search_lower in contract.order_id.lower()
                            or search_lower in contract.contract_number.lower()
                            or search_lower in str(contract.booking_details).lower()
                        )

                    if include:
                        contracts.append(contract)
            except Exception as e:
                print(f"Error processing contract {doc.id}: {e}")
                continue

        # Apply pagination
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
            await self._set_document(self.collection.document(contract.id), data)
        else:
            # Create new
            _, doc_ref = await self._add_document(data)
            contract.id = doc_ref.id

        return contract

    async def delete(self, contract_id: str) -> bool:
        """Delete contract by ID"""
        try:
            await self._delete_document(self.collection.document(contract_id))
            return True
        except Exception:
            return False

    async def count_by_status(self, status: str) -> int:
        """Count contracts by status"""
        query = self.collection.where("ContractStatus", "==", status)
        docs = await self._run_query(query)
        return len(docs)

    async def find_overdue(self) -> List[Contract]:
        """Find all overdue contracts"""
        query = self.collection.where(
            filter=FieldFilter("ContractStatus", "in", ["active", "extended"])
        )

        contracts = []
        docs = await self._run_query(query)
        for doc in docs:
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
        docs = await self._run_query(query)
        for doc in docs:
            try:
                contract = self._to_entity(doc.id, doc.to_dict())
                if contract and contract.date_range.end_date <= future_date:
                    contracts.append(contract)
            except Exception:
                continue

        return contracts

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

    def _to_entity(self, doc_id: str, data: Dict[str, Any]) -> Optional[Contract]:
        """Convert Firestore document to Contract entity"""
        try:
            # Clean all Firebase objects in the data first
            cleaned_data = self._clean_firebase_objects(data)

            # Parse dates
            start_date = parse_datetime(cleaned_data.get("start_date"))
            end_date = parse_datetime(cleaned_data.get("end_date"))

            # Parse money values
            booking_cost = Money(
                cleaned_data.get("booking_cost", 0), cleaned_data.get("Currency", "SAR")
            )
            taxes = Money(
                cleaned_data.get("taxes", 0), cleaned_data.get("Currency", "SAR")
            )
            delivery = Money(
                cleaned_data.get("Delivery", 0), cleaned_data.get("Currency", "SAR")
            )
            offers_total = Money(
                cleaned_data.get("offersTotal", 0), cleaned_data.get("Currency", "SAR")
            )
            total_cost = Money(
                cleaned_data.get("total_cost", 0), cleaned_data.get("Currency", "SAR")
            )

            # EXACT Firebase field mapping based on MCP schema:
            # uid: Reference to users collection
            # carID: Reference to cars collection
            # OrderId: order identifier
            # ContractNumber: contract number
            # start_date: Timestamp
            # end_date: Timestamp
            # booking_cost: number
            # total_cost: number
            # taxes: number
            # Currency: "SAR"
            # ContractStatus: "completed", "active", etc.
            # tansaction_info: transaction data (Firebase typo)

            # Extract user_id from Firebase Reference
            user_id = "unknown_user"
            if "uid" in cleaned_data:
                user_id = str(cleaned_data["uid"])

            # Extract car_id from Firebase Reference
            car_id = "unknown_car"
            if "carID" in cleaned_data:
                car_id = str(cleaned_data["carID"])

            # Parse transaction info using exact Firebase schema
            # EXACT Firebase field: "tansaction_info" (Firebase typo)
            transaction_info = None
            trans_data = cleaned_data.get("tansaction_info") or cleaned_data.get(
                "transaction_info"
            )
            if trans_data:
                trans_status = trans_data.get("status", "pending").lower()
                status_mapping = {
                    "paid": PaymentStatus.PAID,
                    "pending": PaymentStatus.PENDING,
                    "failed": PaymentStatus.FAILED,
                    "partial": PaymentStatus.PARTIAL,
                    "refunded": PaymentStatus.REFUNDED,
                }

                transaction_info = TransactionInfo(
                    status=status_mapping.get(trans_status, PaymentStatus.PENDING),
                    transaction_id=trans_data.get("id")
                    or trans_data.get("transaction_id"),
                    payment_method=trans_data.get("type"),
                )

            # Get booking type from BookingDetails using exact Firebase schema
            booking_details = cleaned_data.get("BookingDetails", {})
            booking_type = booking_details.get("BookingType", "Day")
            if booking_type not in ["Day", "Week", "Month"]:
                booking_type = "Day"

            # Map Firebase ContractStatus using exact values from schema
            # EXACT Firebase values: "completed", "active", etc.
            contract_status_mapping = {
                "completed": ContractStatus.COMPLETED,
                "active": ContractStatus.ACTIVE,
                "in progress": ContractStatus.ACTIVE,
                "cancelled": ContractStatus.CANCELLED,
                "extended": ContractStatus.EXTENDED,
            }
            firebase_status = cleaned_data.get("ContractStatus", "active").lower()
            contract_status = contract_status_mapping.get(
                firebase_status, ContractStatus.ACTIVE
            )

            # Map payment status
            payment_status = PaymentStatus.PENDING
            if trans_data and trans_data.get("status"):
                status_mapping = {
                    "PAID": PaymentStatus.PAID,
                    "paid": PaymentStatus.PAID,
                    "pending": PaymentStatus.PENDING,
                    "PENDING": PaymentStatus.PENDING,
                    "failed": PaymentStatus.FAILED,
                    "FAILED": PaymentStatus.FAILED,
                }
                payment_status = status_mapping.get(
                    trans_data.get("status"), PaymentStatus.PENDING
                )

            # Create entity using EXACT Firebase schema
            contract = Contract(
                order_id=cleaned_data.get(
                    "OrderId", f"ORDER_{doc_id[:8]}"
                ),  # EXACT: "OrderId"
                contract_number=cleaned_data.get(
                    "ContractNumber", f"CNT_{doc_id[:8]}"
                ),  # EXACT: "ContractNumber"
                user_id=user_id,
                car_id=car_id,
                booking_id=cleaned_data.get("booking_id"),  # May not exist in Firebase
                date_range=DateRange(start_date, end_date),
                booking_type=booking_type,
                count=cleaned_data.get("count", 1),  # EXACT: "count"
                booking_cost=booking_cost,  # EXACT: "booking_cost"
                taxes=taxes,  # EXACT: "taxes"
                delivery_fee=delivery,  # EXACT: "Delivery"
                offers_total=offers_total,  # EXACT: "offersTotal"
                total_cost=total_cost,  # EXACT: "total_cost"
                status=contract_status,
                payment_status=payment_status,
                transaction_info=transaction_info,
                is_extended=cleaned_data.get("IsExtended", False),  # May not exist
                booking_details=booking_details,  # EXACT: "BookingDetails"
            )

            # Set the document ID and timestamps using exact Firebase schema
            contract.id = doc_id
            # EXACT Firebase fields: "created_at" and "updated_at" (Timestamps)
            if cleaned_data.get("created_at"):
                contract.created_at = parse_datetime(cleaned_data["created_at"])
            if cleaned_data.get("updated_at"):
                contract.updated_at = parse_datetime(cleaned_data["updated_at"])

            return contract

        except Exception as e:
            print(f"Error converting document to Contract entity: {e}")
            import traceback

            traceback.print_exc()
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
