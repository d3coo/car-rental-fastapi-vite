"""
App Settings Entity
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Simple dataclass, no need for base Entity


@dataclass
class AppSettings:
    """Application-wide settings entity"""

    id: str
    active_main_discount: bool
    main_discount: float  # The actual discount percentage (0-100)
    # Legacy fields for backward compatibility
    home_screen_day_discount: Optional[float] = None
    home_screen_week_discount: Optional[float] = None
    home_screen_month_discount: Optional[float] = None

    @property
    def effective_discount(self) -> float:
        """Get the effective discount based on active status"""
        return self.main_discount if self.active_main_discount else 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "settings": {
                "activeMainDiscount": self.active_main_discount,
                "mainDiscount": {"dayDiscount": self.main_discount},
                "homeScreenDayDiscount": self.home_screen_day_discount
                or self.main_discount,
                "homeScreenWeekDiscount": self.home_screen_week_discount
                or self.main_discount,
                "homeScreenMonthDiscount": self.home_screen_month_discount
                or self.main_discount,
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AppSettings":
        """Create from dictionary"""
        settings = data.get("settings", {})
        main_discount_obj = settings.get("mainDiscount", {})

        return cls(
            id=data.get("id", ""),
            active_main_discount=settings.get("activeMainDiscount", False),
            main_discount=main_discount_obj.get("dayDiscount", 0),
            home_screen_day_discount=settings.get("homeScreenDayDiscount"),
            home_screen_week_discount=settings.get("homeScreenWeekDiscount"),
            home_screen_month_discount=settings.get("homeScreenMonthDiscount"),
        )
