"""
Mock implementation of Contract repository for testing and fallback
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.domain.entities.contract import Contract, ContractStatus, PaymentStatus
from app.domain.repositories.contract_repository import ContractRepository
from app.domain.value_objects.date_range import DateRange
from app.domain.value_objects.money import Money


class MockContractRepository(ContractRepository):
    """Mock implementation of Contract repository"""

    def __init__(self):
        # Sample mock data
        self._contracts: Dict[str, Contract] = {}
        self._populate_mock_data()

    def _populate_mock_data(self):
        """Populate with sample contract data"""
        # Create a sample contract
        sample_contract = Contract(
            order_id="ORDER_001",
            contract_number="CNT_001",
            user_id="user_123",
            car_id="car_456",
            date_range=DateRange(
                start_date=datetime.now(), end_date=datetime.now() + timedelta(days=7)
            ),
            booking_type="Week",
            count=1,
            booking_cost=Money(700, "SAR"),
            taxes=Money(105, "SAR"),
            delivery_fee=Money(50, "SAR"),
            offers_total=Money(0, "SAR"),
            total_cost=Money(855, "SAR"),
            status=ContractStatus.ACTIVE,
            payment_status=PaymentStatus.PAID,
            booking_details={
                "BookingType": "Week",
                "pickup_location": "Riyadh Airport",
                "dropoff_location": "Riyadh Airport",
            },
        )
        # Set the ID manually after creation
        sample_contract.id = "contract_1"
        self._contracts[sample_contract.id] = sample_contract

    async def find_by_id(self, contract_id: str) -> Optional[Contract]:
        """Find contract by ID"""
        return self._contracts.get(contract_id)

    async def find_by_order_id(self, order_id: str) -> Optional[Contract]:
        """Find contract by order ID"""
        for contract in self._contracts.values():
            if contract.order_id == order_id:
                return contract
        return None

    async def find_by_contract_number(self, contract_number: str) -> Optional[Contract]:
        """Find contract by contract number"""
        for contract in self._contracts.values():
            if contract.contract_number == contract_number:
                return contract
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
        contracts = list(self._contracts.values())

        # Apply filters
        if status and status != "all":
            contracts = [c for c in contracts if c.status.value == status]

        if payment_status and payment_status != "all":
            contracts = [
                c for c in contracts if c.payment_status.value == payment_status
            ]

        if user_id:
            contracts = [c for c in contracts if c.user_id == user_id]

        if date_from:
            contracts = [c for c in contracts if c.date_range.start_date >= date_from]

        if date_to:
            contracts = [c for c in contracts if c.date_range.start_date <= date_to]

        if search:
            search_lower = search.lower()
            contracts = [
                c
                for c in contracts
                if search_lower in c.order_id.lower()
                or search_lower in c.contract_number.lower()
            ]

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
        if not contract.id or contract.id == "new":
            # Generate new ID for mock
            contract.id = f"contract_{len(self._contracts) + 1}"

        self._contracts[contract.id] = contract
        return contract

    async def delete(self, contract_id: str) -> bool:
        """Delete contract by ID"""
        if contract_id in self._contracts:
            del self._contracts[contract_id]
            return True
        return False

    async def count_by_status(self, status: str) -> int:
        """Count contracts by status"""
        return len([c for c in self._contracts.values() if c.status.value == status])

    async def find_overdue(self) -> List[Contract]:
        """Find all overdue contracts"""
        return [c for c in self._contracts.values() if c.is_overdue()]

    async def find_expiring_soon(self, days: int = 7) -> List[Contract]:
        """Find contracts expiring within specified days"""
        future_date = datetime.now() + timedelta(days=days)
        return [
            c
            for c in self._contracts.values()
            if c.status in [ContractStatus.ACTIVE, ContractStatus.EXTENDED]
            and c.date_range.end_date <= future_date
        ]
