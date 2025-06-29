"""
Offer Entity
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

# Simple dataclasses, no need for base Entity


@dataclass
class OfferItem:
    """Individual offer item added to a contract or booking"""

    offer: str  # English name
    offer_ar: str  # Arabic name
    offer_type: str  # Type/category of the offer
    offer_price: float  # Unit price
    offer_total_price: float  # Total price
    offer_ref: str  # Reference to Offers collection document
    payment_method: Optional[str] = None  # wallet, custom, etc.
    amount_type: Optional[str] = None  # Type of amount calculation
    custom_amount: Optional[float] = None  # Custom amount if payment method is 'custom'
    offer_end_date: Optional[datetime] = None  # End date for specific offer types

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "offer": self.offer,
            "offerAr": self.offer_ar,
            "offerType": self.offer_type,
            "offerPrice": self.offer_price,
            "offerTotalPrice": self.offer_total_price,
            "offerRef": self.offer_ref,
        }

        # Add optional fields
        if self.payment_method:
            data["paymentMethod"] = self.payment_method
        if self.amount_type:
            data["amountType"] = self.amount_type
        if self.custom_amount is not None:
            data["customAmount"] = self.custom_amount
        if self.offer_end_date:
            data["offerEndDate"] = self.offer_end_date

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OfferItem":
        """Create from dictionary"""
        return cls(
            offer=data.get("offer", ""),
            offer_ar=data.get("offerAr", ""),
            offer_type=data.get("offerType", ""),
            offer_price=float(data.get("offerPrice", 0)),
            offer_total_price=float(data.get("offerTotalPrice", 0)),
            offer_ref=data.get("offerRef", ""),
            payment_method=data.get("paymentMethod"),
            amount_type=data.get("amountType"),
            custom_amount=(
                float(data.get("customAmount"))
                if data.get("customAmount") is not None
                else None
            ),
            offer_end_date=data.get("offerEndDate"),
        )


@dataclass
class OfferHistory:
    """History entry for offer modifications"""

    action: str  # 'add' or 'remove'
    offers: list  # List of offers affected
    amount: float  # Financial impact
    payment_method: str  # Payment method used
    timestamp: str  # ISO timestamp
    user_id: str  # User who performed action

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action": self.action,
            "offers": self.offers,
            "amount": self.amount,
            "paymentMethod": self.payment_method,
            "timestamp": self.timestamp,
            "userId": self.user_id,
        }
