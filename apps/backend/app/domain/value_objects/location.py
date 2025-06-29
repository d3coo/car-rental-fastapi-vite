"""
Location value objects for handling different location types
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LocationType(Enum):
    """Types of locations"""

    BRANCH = "branch"
    AIRPORT = "airport"
    SAVED_ADDRESS = "saved_address"
    SAME_AS_PICKUP = "same"


@dataclass(frozen=True)
class Location:
    """Base location value object"""

    type: LocationType
    name: str
    id: Optional[str] = None

    def is_same_as(self, other: "Location") -> bool:
        """Check if two locations are the same"""
        return self.type == other.type and self.id == other.id


@dataclass(frozen=True)
class BranchLocation(Location):
    """Branch location"""

    def __init__(self, branch_data: dict):
        super().__init__(
            type=LocationType.BRANCH,
            name=branch_data.get("name", ""),
            id=branch_data.get("id"),
        )
        object.__setattr__(self, "branch_data", branch_data)


@dataclass(frozen=True)
class AirportLocation(Location):
    """Airport location"""

    def __init__(self, airport_data: dict):
        super().__init__(
            type=LocationType.AIRPORT,
            name=airport_data.get("name", ""),
            id=airport_data.get("id"),
        )
        object.__setattr__(self, "airport_data", airport_data)


@dataclass(frozen=True)
class SavedAddressLocation(Location):
    """Saved address location"""

    def __init__(self, address_data: dict):
        super().__init__(
            type=LocationType.SAVED_ADDRESS,
            name=address_data.get("name", ""),
            id=address_data.get("id"),
        )
        object.__setattr__(self, "address_data", address_data)


@dataclass(frozen=True)
class LocationPair:
    """Pickup and dropoff location pair"""

    pickup: Location
    dropoff: Location

    @property
    def is_same_location(self) -> bool:
        """Check if pickup and dropoff are the same"""
        return self.pickup.is_same_as(self.dropoff)

    @classmethod
    def from_booking_data(cls, booking_details: dict) -> "LocationPair":
        """Create from booking details data"""
        # Determine pickup location
        if booking_details.get("isPickup"):
            pickup = BranchLocation(booking_details.get("PicupBranche", {}))
        elif booking_details.get("isAirport"):
            pickup = AirportLocation(booking_details.get("Ariport", {}))
        elif booking_details.get("isSavedAddress"):
            pickup = SavedAddressLocation(booking_details.get("SavedAddress", {}))
        else:
            pickup = Location(LocationType.BRANCH, "Unknown")

        # Determine dropoff location
        return_branch = booking_details.get("ReturnBranche", {})
        return_airport = booking_details.get("ReturnAirport", {})
        return_saved = booking_details.get("ReturnSavedAddress", {})

        if return_branch:
            dropoff = BranchLocation(return_branch)
        elif return_airport:
            dropoff = AirportLocation(return_airport)
        elif return_saved:
            dropoff = SavedAddressLocation(return_saved)
        else:
            dropoff = pickup  # Same as pickup

        return cls(pickup, dropoff)
