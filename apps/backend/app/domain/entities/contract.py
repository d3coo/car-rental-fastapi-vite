"""
Contract entity - Core business object for rental contracts
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..base import BusinessRuleViolation, Entity, ValidationError
from ..value_objects.date_range import DateRange
from ..value_objects.money import Money


class ContractStatus(Enum):
    """Contract status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXTENDED = "extended"


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class ExtensionDetails:
    """Details of a contract extension"""

    extended_date: datetime
    new_end_date: datetime
    extension_cost: Money
    extension_type: str  # 'Day', 'Week', 'Month'
    count: int
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class TransactionInfo:
    """Transaction information"""

    status: PaymentStatus
    transaction_id: Optional[str] = None
    payment_method: Optional[str] = None
    amount: Optional[Money] = None
    timestamp: Optional[datetime] = None


@dataclass
class Contract(Entity):
    """Contract entity with business logic"""

    order_id: str
    contract_number: str
    user_id: str
    car_id: str
    date_range: DateRange
    booking_type: str  # 'Day', 'Week', 'Month'
    count: int
    booking_cost: Money
    taxes: Money
    delivery_fee: Money
    offers_total: Money
    total_cost: Money
    booking_id: Optional[str] = None

    # Status
    status: ContractStatus = ContractStatus.ACTIVE
    payment_status: PaymentStatus = PaymentStatus.PENDING
    transaction_info: Optional[TransactionInfo] = None

    # Extension tracking
    is_extended: bool = False
    extension_history: List[ExtensionDetails] = field(default_factory=list)

    # Metadata inherited from Entity base class

    # Additional data (flexible storage)
    booking_details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate contract after creation"""
        super().__post_init__()
        self.validate()

    def validate(self):
        """Validate contract business rules"""
        if not self.order_id or not self.order_id.strip():
            raise ValidationError("Order ID is required")

        if not self.contract_number or not self.contract_number.strip():
            raise ValidationError("Contract number is required")

        if not self.user_id or not self.user_id.strip():
            raise ValidationError("User ID is required")

        if not self.car_id or not self.car_id.strip():
            raise ValidationError("Car ID is required")

        if self.count <= 0:
            raise ValidationError("Count must be positive")

        if self.booking_type not in ["Day", "Week", "Month"]:
            raise ValidationError("Booking type must be Day, Week, or Month")

        # Validate money amounts are not negative
        if self.booking_cost.amount < 0:
            raise ValidationError("Booking cost cannot be negative")

        if self.total_cost.amount < 0:
            raise ValidationError("Total cost cannot be negative")

    def can_extend(self) -> bool:
        """Check if contract can be extended"""
        return self.status == ContractStatus.ACTIVE and self.payment_status in [
            PaymentStatus.PAID,
            PaymentStatus.PARTIAL,
        ]

    def extend(
        self,
        new_end_date: datetime,
        extension_cost: Money,
        extension_type: str,
        count: int,
    ) -> None:
        """Extend the contract"""
        if not self.can_extend():
            raise BusinessRuleViolation("Contract cannot be extended in current state")

        if new_end_date <= self.date_range.end_date:
            raise ValidationError("Extension date must be after current end date")

        if extension_type not in ["Day", "Week", "Month"]:
            raise ValidationError("Extension type must be Day, Week, or Month")

        if count <= 0:
            raise ValidationError("Extension count must be positive")

        if extension_cost.amount < 0:
            raise ValidationError("Extension cost cannot be negative")

        # Create extension record
        extension = ExtensionDetails(
            extended_date=datetime.now(),
            new_end_date=new_end_date,
            extension_cost=extension_cost,
            extension_type=extension_type,
            count=count,
        )

        # Update contract
        self.date_range = self.date_range.extend_to(new_end_date)
        self.total_cost = self.total_cost.add(extension_cost)
        self.is_extended = True
        self.extension_history.append(extension)
        self.mark_updated()

        if self.status == ContractStatus.ACTIVE:
            self.status = ContractStatus.EXTENDED

    def complete(self) -> None:
        """Mark contract as completed"""
        if self.status not in [ContractStatus.ACTIVE, ContractStatus.EXTENDED]:
            raise BusinessRuleViolation(
                "Only active or extended contracts can be completed"
            )

        if self.payment_status not in [PaymentStatus.PAID]:
            raise BusinessRuleViolation("Contract must be fully paid before completion")

        self.status = ContractStatus.COMPLETED
        self.mark_updated()

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the contract"""
        if self.status == ContractStatus.COMPLETED:
            raise BusinessRuleViolation("Cannot cancel a completed contract")

        if not reason or not reason.strip():
            raise ValidationError("Cancellation reason is required")

        self.status = ContractStatus.CANCELLED
        self.mark_updated()

        self.booking_details["cancellation_reason"] = reason
        self.booking_details["cancelled_at"] = datetime.now().isoformat()

    def update_payment_status(
        self, status: PaymentStatus, transaction_info: Optional[TransactionInfo] = None
    ) -> None:
        """Update payment status"""
        # Business rule: Cannot change status of cancelled contracts
        if self.status == ContractStatus.CANCELLED:
            raise BusinessRuleViolation(
                "Cannot update payment status of cancelled contract"
            )

        self.payment_status = status
        if transaction_info:
            self.transaction_info = transaction_info
        self.mark_updated()

    def calculate_remaining_days(self) -> int:
        """Calculate remaining days in contract"""
        if self.status not in [ContractStatus.ACTIVE, ContractStatus.EXTENDED]:
            return 0

        remaining = (self.date_range.end_date - datetime.now()).days
        return max(0, remaining)

    def is_overdue(self) -> bool:
        """Check if contract is overdue"""
        return (
            self.status in [ContractStatus.ACTIVE, ContractStatus.EXTENDED]
            and datetime.now() > self.date_range.end_date
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "OrderId": self.order_id,
            "ContractNumber": self.contract_number,
            "user_id": self.user_id,
            "car_id": self.car_id,
            "booking_id": self.booking_id,
            "start_date": self.date_range.start_date.isoformat(),
            "end_date": self.date_range.end_date.isoformat(),
            "count": self.count,
            "BookingType": self.booking_type,
            "booking_cost": self.booking_cost.to_float(),
            "taxes": self.taxes.to_float(),
            "Delivery": self.delivery_fee.to_float(),
            "offersTotal": self.offers_total.to_float(),
            "total_cost": self.total_cost.to_float(),
            "Currency": self.total_cost.currency,
            "ContractStatus": self.status.value,
            "payment_status": self.payment_status.value,
            "IsExtended": self.is_extended,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "BookingDetails": self.booking_details,
            "transaction_info": (
                {
                    "status": self.transaction_info.status.value,
                    "transaction_id": self.transaction_info.transaction_id,
                    "payment_method": self.transaction_info.payment_method,
                }
                if self.transaction_info
                else None
            ),
            "listExtendDetails": (
                [
                    {
                        "extended_date": ext.extended_date.isoformat(),
                        "new_end_date": ext.new_end_date.isoformat(),
                        "extension_cost": ext.extension_cost.to_float(),
                        "extension_type": ext.extension_type,
                        "count": ext.count,
                        "created_at": ext.created_at.isoformat(),
                    }
                    for ext in self.extension_history
                ]
                if self.extension_history
                else []
            ),
        }
