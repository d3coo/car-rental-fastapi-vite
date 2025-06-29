"""
Car entity - Core business object for vehicle management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..base import BusinessRuleViolation, Entity, ValidationError
from ..value_objects.money import Money


class CarStatus(Enum):
    """Car status enumeration"""

    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class FuelType(Enum):
    """Fuel type enumeration"""

    GASOLINE = "gasoline"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"


class TransmissionType(Enum):
    """Transmission type enumeration"""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    CVT = "cvt"


@dataclass
class Car(Entity):
    """Car entity with business logic"""

    make: str
    model: str
    year: int
    color: str
    license_plate: str
    category: str

    # Pricing
    daily_rate: Money
    weekly_rate: Optional[Money] = None
    monthly_rate: Optional[Money] = None

    # Status and location
    status: CarStatus = CarStatus.AVAILABLE
    location: Optional[str] = None

    # Technical specifications
    mileage: Optional[int] = None
    fuel_type: Optional[FuelType] = None
    transmission: Optional[TransmissionType] = None
    seats: Optional[int] = None
    engine_size: Optional[str] = None

    # Features and amenities
    features: List[str] = field(default_factory=list)
    has_gps: bool = False
    has_bluetooth: bool = False
    has_usb_charger: bool = False
    has_backup_camera: bool = False

    # Maintenance and service
    last_service_date: Optional[datetime] = None
    next_service_date: Optional[datetime] = None
    service_interval_km: Optional[int] = None

    # Additional flexible data
    car_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate car after creation"""
        super().__post_init__()
        self.validate()

    def validate(self):
        """Validate car business rules"""
        self._validate_basic_info()
        self._validate_rates()
        self._validate_technical_specs()

    def _validate_basic_info(self):
        """Validate basic car information"""
        if not self.make or not self.make.strip():
            raise ValidationError("Car make is required")

        if not self.model or not self.model.strip():
            raise ValidationError("Car model is required")

        if self.year < 1900 or self.year > datetime.now().year + 2:
            raise ValidationError(
                f"Car year must be between 1900 and {datetime.now().year + 2}"
            )

        if not self.color or not self.color.strip():
            raise ValidationError("Car color is required")

        if not self.license_plate or not self.license_plate.strip():
            raise ValidationError("License plate is required")

        if not self.category or not self.category.strip():
            raise ValidationError("Car category is required")

    def _validate_rates(self):
        """Validate pricing rates"""
        if self.daily_rate.amount <= 0:
            raise ValidationError("Daily rate must be positive")

        if self.weekly_rate and self.weekly_rate.amount <= 0:
            raise ValidationError("Weekly rate must be positive")

        if self.monthly_rate and self.monthly_rate.amount <= 0:
            raise ValidationError("Monthly rate must be positive")

    def _validate_technical_specs(self):
        """Validate technical specifications"""
        if self.mileage is not None and self.mileage < 0:
            raise ValidationError("Mileage cannot be negative")

        if self.seats is not None and (self.seats < 1 or self.seats > 50):
            raise ValidationError("Seats must be between 1 and 50")

        if self.service_interval_km is not None and self.service_interval_km <= 0:
            raise ValidationError("Service interval must be positive")

    def is_available(self) -> bool:
        """Check if car is available for booking"""
        return self.status == CarStatus.AVAILABLE

    def is_overdue_for_service(self) -> bool:
        """Check if car is overdue for service"""
        if not self.next_service_date:
            return False
        return datetime.now() > self.next_service_date

    def mark_as_rented(self) -> None:
        """Mark car as rented"""
        if not self.is_available():
            raise BusinessRuleViolation("Car is not available for rental")

        self.status = CarStatus.RENTED
        self.mark_updated()

    def mark_as_available(self) -> None:
        """Mark car as available"""
        if self.status == CarStatus.OUT_OF_SERVICE:
            raise BusinessRuleViolation("Cannot make out-of-service car available")

        self.status = CarStatus.AVAILABLE
        self.mark_updated()

    def send_for_maintenance(self, reason: Optional[str] = None) -> None:
        """Send car for maintenance"""
        if self.status == CarStatus.RENTED:
            raise BusinessRuleViolation("Cannot send rented car for maintenance")

        self.status = CarStatus.MAINTENANCE
        if reason:
            self.car_data["maintenance_reason"] = reason
            self.car_data["maintenance_started"] = datetime.now().isoformat()
        self.mark_updated()

    def complete_maintenance(
        self,
        mileage: Optional[int] = None,
        next_service_date: Optional[datetime] = None,
    ) -> None:
        """Complete maintenance and mark as available"""
        if self.status != CarStatus.MAINTENANCE:
            raise BusinessRuleViolation("Car is not in maintenance")

        if mileage is not None:
            if mileage < (self.mileage or 0):
                raise ValidationError("New mileage cannot be less than current mileage")
            self.mileage = mileage

        if next_service_date:
            self.next_service_date = next_service_date

        self.last_service_date = datetime.now()
        self.status = CarStatus.AVAILABLE

        # Clear maintenance data
        self.car_data.pop("maintenance_reason", None)
        self.car_data.pop("maintenance_started", None)
        self.car_data["last_maintenance_completed"] = datetime.now().isoformat()

        self.mark_updated()

    def put_out_of_service(self, reason: str) -> None:
        """Put car out of service"""
        if not reason or not reason.strip():
            raise ValidationError("Reason for out of service is required")

        if self.status == CarStatus.RENTED:
            raise BusinessRuleViolation("Cannot put rented car out of service")

        self.status = CarStatus.OUT_OF_SERVICE
        self.car_data["out_of_service_reason"] = reason
        self.car_data["out_of_service_date"] = datetime.now().isoformat()
        self.mark_updated()

    def return_to_service(self) -> None:
        """Return car to service"""
        if self.status != CarStatus.OUT_OF_SERVICE:
            raise BusinessRuleViolation("Car is not out of service")

        self.status = CarStatus.AVAILABLE

        # Clear out of service data
        self.car_data.pop("out_of_service_reason", None)
        self.car_data.pop("out_of_service_date", None)
        self.car_data["returned_to_service_date"] = datetime.now().isoformat()

        self.mark_updated()

    def add_feature(self, feature: str) -> None:
        """Add a feature to the car"""
        if not feature or not feature.strip():
            raise ValidationError("Feature name cannot be empty")

        feature = feature.strip()
        if feature not in self.features:
            self.features.append(feature)
            self.mark_updated()

    def remove_feature(self, feature: str) -> None:
        """Remove a feature from the car"""
        if feature in self.features:
            self.features.remove(feature)
            self.mark_updated()

    def update_rates(
        self,
        daily_rate: Optional[Money] = None,
        weekly_rate: Optional[Money] = None,
        monthly_rate: Optional[Money] = None,
    ) -> None:
        """Update pricing rates"""
        if daily_rate is not None:
            if daily_rate.amount <= 0:
                raise ValidationError("Daily rate must be positive")
            self.daily_rate = daily_rate

        if weekly_rate is not None:
            if weekly_rate.amount <= 0:
                raise ValidationError("Weekly rate must be positive")
            self.weekly_rate = weekly_rate

        if monthly_rate is not None:
            if monthly_rate.amount <= 0:
                raise ValidationError("Monthly rate must be positive")
            self.monthly_rate = monthly_rate

        self.mark_updated()

    def get_rate_for_booking_type(self, booking_type: str) -> Money:
        """Get rate for specific booking type"""
        if booking_type == "Day":
            return self.daily_rate
        elif booking_type == "Week":
            return self.weekly_rate or self.daily_rate.multiply(7)
        elif booking_type == "Month":
            return self.monthly_rate or self.daily_rate.multiply(30)
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

    @property
    def display_name(self) -> str:
        """Get car display name"""
        return f"{self.year} {self.make} {self.model}"

    @property
    def age_years(self) -> int:
        """Get car age in years"""
        return datetime.now().year - self.year

    @property
    def is_new(self) -> bool:
        """Check if car is considered new (less than 2 years old)"""
        return self.age_years < 2

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "color": self.color,
            "license_plate": self.license_plate,
            "category": self.category,
            "display_name": self.display_name,
            "age_years": self.age_years,
            "is_new": self.is_new,
            "daily_rate": self.daily_rate.to_float(),
            "weekly_rate": self.weekly_rate.to_float() if self.weekly_rate else None,
            "monthly_rate": self.monthly_rate.to_float() if self.monthly_rate else None,
            "currency": self.daily_rate.currency,
            "status": self.status.value,
            "is_available": self.is_available(),
            "location": self.location,
            "mileage": self.mileage,
            "fuel_type": self.fuel_type.value if self.fuel_type else None,
            "transmission": self.transmission.value if self.transmission else None,
            "seats": self.seats,
            "engine_size": self.engine_size,
            "features": self.features,
            "has_gps": self.has_gps,
            "has_bluetooth": self.has_bluetooth,
            "has_usb_charger": self.has_usb_charger,
            "has_backup_camera": self.has_backup_camera,
            "last_service_date": (
                self.last_service_date.isoformat() if self.last_service_date else None
            ),
            "next_service_date": (
                self.next_service_date.isoformat() if self.next_service_date else None
            ),
            "service_interval_km": self.service_interval_km,
            "is_overdue_for_service": self.is_overdue_for_service(),
            "car_data": self.car_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
