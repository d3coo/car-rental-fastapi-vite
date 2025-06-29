"""
Booking entity - Business object for rental bookings
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from ..base import BusinessRuleViolation, Entity, ValidationError
from ..value_objects.date_range import DateRange
from ..value_objects.location import LocationPair
from ..value_objects.money import Money


class BookingStatus(Enum):
    """Booking status enumeration"""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACCEPTED = "accepted"
    DENIED = "denied"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class PaymentStatus(Enum):
    """Payment status enumeration"""

    PENDING = "pending"
    PAID = "paid"
    PARTIAL = "partial"
    FAILED = "failed"
    REFUNDED = "refunded"


@dataclass
class Booking(Entity):
    """Booking entity with business logic"""

    order_id: str
    booking_number: str
    user_id: str
    car_id: str
    date_range: DateRange
    booking_type: str  # 'Day', 'Week', 'Month'
    count: int
    locations: LocationPair
    booking_cost: Money
    taxes: Money
    delivery_fee: Money
    offers_total: Money
    total_cost: Money

    # Package booking specific
    is_package_booking: bool = False
    package_months: Optional[int] = None

    # Installment specific
    is_installment: bool = False

    # Status
    status: BookingStatus = BookingStatus.PENDING
    payment_status: PaymentStatus = PaymentStatus.PENDING

    # Approval workflow
    denied_reason: Optional[str] = None
    accepted_at: Optional[datetime] = None
    denied_at: Optional[datetime] = None

    # Additional data
    booking_details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate booking after creation"""
        super().__post_init__()
        self.validate()

    def validate(self):
        """Validate booking business rules"""
        if not self.order_id or not self.order_id.strip():
            raise ValidationError("Order ID is required")

        if not self.booking_number or not self.booking_number.strip():
            raise ValidationError("Booking number is required")

        if not self.user_id or not self.user_id.strip():
            raise ValidationError("User ID is required")

        if not self.car_id or not self.car_id.strip():
            raise ValidationError("Car ID is required")

        if self.count <= 0:
            raise ValidationError("Count must be positive")

        if self.booking_type not in ["Day", "Week", "Month"]:
            raise ValidationError("Booking type must be Day, Week, or Month")

        if self.is_package_booking and (
            not self.package_months or self.package_months <= 0
        ):
            raise ValidationError(
                "Package months must be positive for package bookings"
            )

        # Validate money amounts
        if self.booking_cost.amount < 0:
            raise ValidationError("Booking cost cannot be negative")

        if self.total_cost.amount < 0:
            raise ValidationError("Total cost cannot be negative")

    def can_accept(self) -> bool:
        """Check if booking can be accepted"""
        return self.status == BookingStatus.PENDING

    def can_deny(self) -> bool:
        """Check if booking can be denied"""
        return self.status == BookingStatus.PENDING

    def can_cancel(self) -> bool:
        """Check if booking can be cancelled"""
        return self.status in [
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.ACCEPTED,
        ]

    def accept(self) -> None:
        """Accept the booking"""
        if not self.can_accept():
            raise BusinessRuleViolation("Booking cannot be accepted in current state")

        self.status = BookingStatus.ACCEPTED
        self.accepted_at = datetime.now()
        self.mark_updated()

    def deny(self, reason: str) -> None:
        """Deny the booking"""
        if not self.can_deny():
            raise BusinessRuleViolation("Booking cannot be denied in current state")

        if not reason or not reason.strip():
            raise ValidationError("Denial reason is required")

        self.status = BookingStatus.DENIED
        self.denied_reason = reason
        self.denied_at = datetime.now()
        self.mark_updated()

    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the booking"""
        if not self.can_cancel():
            raise BusinessRuleViolation("Booking cannot be cancelled in current state")

        self.status = BookingStatus.CANCELLED
        self.mark_updated()

        if reason:
            self.booking_details["cancellation_reason"] = reason
            self.booking_details["cancelled_at"] = datetime.now().isoformat()

    def update_dates(self, new_date_range: DateRange) -> None:
        """Update booking dates"""
        if self.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise BusinessRuleViolation(
                "Cannot update dates after booking is processed"
            )

        self.date_range = new_date_range
        self.mark_updated()

    def update_car(
        self, new_car_id: str, new_booking_cost: Money, new_total_cost: Money
    ) -> None:
        """Replace car in booking"""
        if self.status not in [
            BookingStatus.PENDING,
            BookingStatus.CONFIRMED,
            BookingStatus.ACCEPTED,
        ]:
            raise BusinessRuleViolation("Cannot replace car in current booking state")

        if not new_car_id or not new_car_id.strip():
            raise ValidationError("New car ID is required")

        if new_booking_cost.amount < 0:
            raise ValidationError("New booking cost cannot be negative")

        if new_total_cost.amount < 0:
            raise ValidationError("New total cost cannot be negative")

        self.car_id = new_car_id
        self.booking_cost = new_booking_cost
        self.total_cost = new_total_cost
        self.mark_updated()

    def update_locations(self, new_locations: LocationPair) -> None:
        """Update pickup and dropoff locations"""
        if self.status not in [BookingStatus.PENDING, BookingStatus.CONFIRMED]:
            raise BusinessRuleViolation(
                "Cannot update locations after booking is processed"
            )

        self.locations = new_locations
        self.mark_updated()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "OrderId": self.order_id,
            "BookingNumber": self.booking_number,
            "user_id": self.user_id,
            "car_id": self.car_id,
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
            "OrderStatus": self.status.value,
            "payment_status": self.payment_status.value,
            "isPackageBooking": self.is_package_booking,
            "packageMonths": self.package_months,
            "isInstallment": self.is_installment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "BookingDetails": self.booking_details,
            "denied_reason": self.denied_reason,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "denied_at": self.denied_at.isoformat() if self.denied_at else None,
        }
