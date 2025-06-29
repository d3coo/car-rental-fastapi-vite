"""
User entity - Core business object for user management
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..base import BusinessRuleViolation, Entity, ValidationError
from ..value_objects.money import Money


class UserStatus(Enum):
    """User status enumeration"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


@dataclass
class SavedAddress:
    """User's saved address"""

    id: str
    name: str
    address: str
    city: str
    coordinates: Optional[Dict[str, float]] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "city": self.city,
            "coordinates": self.coordinates,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class User(Entity):
    """User entity with business logic"""

    email: str
    first_name: str
    last_name: str
    phone_number: str
    nationality: str
    status_number: str  # ID/Passport number

    # Status
    status: UserStatus = UserStatus.PENDING_VERIFICATION

    # Wallet
    wallet_balance: Money = field(default_factory=lambda: Money(0, "SAR"))

    # Preferences
    preferred_language: str = "en"

    # Verification
    email_verified: bool = False
    phone_verified: bool = False

    # Saved addresses
    saved_addresses: List[SavedAddress] = field(default_factory=list)

    # Additional flexible data
    user_data: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate user after creation"""
        super().__post_init__()
        self.validate()

    def validate(self):
        """Validate user business rules"""
        if not self.email or not self.email.strip():
            raise ValidationError("Email is required")

        if "@" not in self.email:
            raise ValidationError("Email must be valid")

        if not self.first_name or not self.first_name.strip():
            raise ValidationError("First name is required")

        if not self.last_name or not self.last_name.strip():
            raise ValidationError("Last name is required")

        if not self.phone_number or not self.phone_number.strip():
            raise ValidationError("Phone number is required")

        if not self.nationality or not self.nationality.strip():
            raise ValidationError("Nationality is required")

        if not self.status_number or not self.status_number.strip():
            raise ValidationError("Status number (ID/Passport) is required")

        if self.wallet_balance.amount < 0:
            raise ValidationError("Wallet balance cannot be negative")

        if self.preferred_language not in ["en", "ar"]:
            raise ValidationError("Preferred language must be 'en' or 'ar'")

    def can_make_bookings(self) -> bool:
        """Check if user can make bookings"""
        return (
            self.status == UserStatus.ACTIVE
            and self.email_verified
            and self.phone_verified
        )

    def activate(self) -> None:
        """Activate user account"""
        if not self.email_verified or not self.phone_verified:
            raise BusinessRuleViolation("User must be verified before activation")

        if self.status == UserStatus.SUSPENDED:
            raise BusinessRuleViolation("Cannot activate suspended user")

        self.status = UserStatus.ACTIVE
        self.mark_updated()

    def suspend(self, reason: str) -> None:
        """Suspend user account"""
        if not reason or not reason.strip():
            raise ValidationError("Suspension reason is required")

        if self.status == UserStatus.SUSPENDED:
            raise BusinessRuleViolation("User is already suspended")

        self.status = UserStatus.SUSPENDED
        self.user_data["suspension_reason"] = reason
        self.user_data["suspended_at"] = datetime.now().isoformat()
        self.mark_updated()

    def deactivate(self) -> None:
        """Deactivate user account"""
        if self.status == UserStatus.SUSPENDED:
            raise BusinessRuleViolation("Cannot deactivate suspended user")

        self.status = UserStatus.INACTIVE
        self.mark_updated()

    def verify_email(self) -> None:
        """Mark email as verified"""
        self.email_verified = True
        self.mark_updated()

        # Auto-activate if both email and phone are verified
        if self.phone_verified and self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE

    def verify_phone(self) -> None:
        """Mark phone as verified"""
        self.phone_verified = True
        self.mark_updated()

        # Auto-activate if both email and phone are verified
        if self.email_verified and self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE

    def add_to_wallet(self, amount: Money) -> None:
        """Add money to wallet"""
        if amount.currency != self.wallet_balance.currency:
            raise ValidationError(
                f"Currency mismatch: wallet is {self.wallet_balance.currency}, "
                f"adding {amount.currency}"
            )

        if amount.amount <= 0:
            raise ValidationError("Amount to add must be positive")

        self.wallet_balance = self.wallet_balance.add(amount)
        self.mark_updated()

    def deduct_from_wallet(self, amount: Money) -> None:
        """Deduct money from wallet"""
        if amount.currency != self.wallet_balance.currency:
            raise ValidationError(
                f"Currency mismatch: wallet is {self.wallet_balance.currency}, "
                f"deducting {amount.currency}"
            )

        if amount.amount <= 0:
            raise ValidationError("Amount to deduct must be positive")

        if self.wallet_balance.amount < amount.amount:
            raise BusinessRuleViolation("Insufficient wallet balance")

        self.wallet_balance = self.wallet_balance.subtract(amount)
        self.mark_updated()

    def add_saved_address(self, address: SavedAddress) -> None:
        """Add a saved address"""
        # Check for duplicate address names
        for existing_addr in self.saved_addresses:
            if existing_addr.name.lower() == address.name.lower():
                raise ValidationError(f"Address name '{address.name}' already exists")

        # Limit number of saved addresses
        if len(self.saved_addresses) >= 10:
            raise BusinessRuleViolation("Maximum 10 saved addresses allowed")

        self.saved_addresses.append(address)
        self.mark_updated()

    def remove_saved_address(self, address_id: str) -> None:
        """Remove a saved address"""
        self.saved_addresses = [
            addr for addr in self.saved_addresses if addr.id != address_id
        ]
        self.mark_updated()

    def get_saved_address(self, address_id: str) -> Optional[SavedAddress]:
        """Get saved address by ID"""
        for address in self.saved_addresses:
            if address.id == address_id:
                return address
        return None

    def update_profile(
        self,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        preferred_language: Optional[str] = None,
    ) -> None:
        """Update user profile information"""
        if first_name is not None:
            if not first_name.strip():
                raise ValidationError("First name cannot be empty")
            self.first_name = first_name.strip()

        if last_name is not None:
            if not last_name.strip():
                raise ValidationError("Last name cannot be empty")
            self.last_name = last_name.strip()

        if phone_number is not None:
            if not phone_number.strip():
                raise ValidationError("Phone number cannot be empty")
            self.phone_number = phone_number.strip()
            # If phone number changed, require re-verification
            self.phone_verified = False

        if preferred_language is not None:
            if preferred_language not in ["en", "ar"]:
                raise ValidationError("Preferred language must be 'en' or 'ar'")
            self.preferred_language = preferred_language

        self.mark_updated()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_verified(self) -> bool:
        """Check if user is fully verified"""
        return self.email_verified and self.phone_verified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone_number": self.phone_number,
            "nationality": self.nationality,
            "status_number": self.status_number,
            "status": self.status.value,
            "wallet_balance": self.wallet_balance.to_float(),
            "wallet_currency": self.wallet_balance.currency,
            "preferred_language": self.preferred_language,
            "email_verified": self.email_verified,
            "phone_verified": self.phone_verified,
            "is_verified": self.is_verified,
            "can_make_bookings": self.can_make_bookings(),
            "saved_addresses": [addr.to_dict() for addr in self.saved_addresses],
            "user_data": self.user_data,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
