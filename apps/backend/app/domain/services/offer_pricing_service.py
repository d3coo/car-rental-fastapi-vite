"""
Enhanced Offer Pricing Service - Complete offer pricing and extension logic
Handles all offer types with proper business rules and pricing calculations
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from ..base import ValidationError
from ..value_objects.money import Money

logger = logging.getLogger(__name__)


class OfferType(Enum):
    """Supported offer types"""

    INSURANCE = "Insurance"
    KM = "KM"
    CHILD_CHAIR = "ChildChair"
    DOCUMENTS = "Documents"


class BookingType(Enum):
    """Supported booking types"""

    DAY = "Day"
    WEEK = "Week"
    MONTH = "Month"


class OfferPricingService:
    """
    Enhanced service for offer pricing and extension calculations
    Implements exact logic from frontend with backend best practices
    """

    TAX_RATE = 0.15  # 15% tax rate
    INSURANCE_PERCENTAGE = 0.20  # 20% of current car price
    KM_PERCENTAGE = 0.25  # 25% of current car price
    DAYS_PER_WEEK = 7
    DAYS_PER_MONTH = 30

    def __init__(self):
        self.external_offer_prices: Dict[str, Dict[str, float]] = {}

    def set_external_offer_prices(
        self, offer_prices: Dict[str, Dict[str, float]]
    ) -> None:
        """
        Set external offer prices (e.g., from API calls)
        Format: {offer_name: {L2: price, L3: price}}
        """
        self.external_offer_prices = offer_prices

    def calculate_current_car_price(
        self,
        car_data: Dict[str, Any],
        booking_type: str,
        has_discount: bool = False,
        discount_percent: float = 0.0,
    ) -> float:
        """
        Calculate current car price considering discounts
        This is the improved logic that uses current pricing instead of original
        """
        booking_type_enum = BookingType(booking_type)

        # Get base price based on booking type
        if booking_type_enum == BookingType.DAY:
            # Check for booked day price first (already discounted price)
            base_price = car_data.get("booked_day_price")
            if base_price:
                return base_price

            # Use rental price with discount
            base_price = car_data.get(
                "rental_price_day", car_data.get("rental_price", 0)
            )
            if has_discount and discount_percent > 0:
                base_price = base_price * (1 - discount_percent / 100)

        elif booking_type_enum == BookingType.WEEK:
            base_price = car_data.get("rental_price_week", 0)
            if has_discount and discount_percent > 0:
                base_price = base_price * (1 - discount_percent / 100)

        elif booking_type_enum == BookingType.MONTH:
            base_price = car_data.get("rental_price_month", 0)
            if has_discount and discount_percent > 0:
                base_price = base_price * (1 - discount_percent / 100)
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

        if base_price <= 0:
            raise ValidationError(f"Invalid car price for booking type {booking_type}")

        return base_price

    def calculate_total_days(self, booking_type: str, units: int) -> int:
        """Calculate total days based on booking type and units"""
        booking_type_enum = BookingType(booking_type)

        if booking_type_enum == BookingType.DAY:
            return units
        elif booking_type_enum == BookingType.WEEK:
            return units * self.DAYS_PER_WEEK
        elif booking_type_enum == BookingType.MONTH:
            return units * self.DAYS_PER_MONTH
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

    def calculate_insurance_offer_price(
        self, current_car_price: float, units: int, currency: str = "SAR"
    ) -> Money:
        """
        Calculate Insurance offer price
        Formula: (current_car_price × units) × 20%
        Uses unit-based calculation (not daily × total_days)
        """
        total_rental_cost = current_car_price * units
        insurance_cost = total_rental_cost * self.INSURANCE_PERCENTAGE

        logger.debug(
            f"Insurance calculation: {current_car_price} × {units} × {self.INSURANCE_PERCENTAGE} = {insurance_cost}"
        )

        return Money(insurance_cost, currency)

    def calculate_km_offer_price(
        self, current_car_price: float, units: int, currency: str = "SAR"
    ) -> Money:
        """
        Calculate KM (Unlimited Kilometers) offer price
        Formula: (current_car_price × units) × 25%
        Uses unit-based calculation (not daily × total_days)
        """
        total_rental_cost = current_car_price * units
        km_cost = total_rental_cost * self.KM_PERCENTAGE

        logger.debug(
            f"KM calculation: {current_car_price} × {units} × {self.KM_PERCENTAGE} = {km_cost}"
        )

        return Money(km_cost, currency)

    def calculate_child_chair_offer_price(
        self,
        offer_data: Dict[str, Any],
        booking_type: str,
        units: int,
        total_days: int,
        currency: str = "SAR",
    ) -> Money:
        """
        Calculate ChildChair offer price with complex logic
        Supports daily rates and L2/L3 pricing for week/month extensions
        """
        booking_type_enum = BookingType(booking_type)
        offer_name = offer_data.get("offer", offer_data.get("name", ""))

        # Get stored external prices if available
        external_prices = self.external_offer_prices.get(offer_name, {})

        if booking_type_enum == BookingType.DAY:
            # Daily calculation: offer_price × units
            daily_price = offer_data.get("offerPrice", offer_data.get("price", 0))
            total_cost = daily_price * units

            logger.debug(
                f"ChildChair daily calculation: {daily_price} × {units} = {total_cost}"
            )

        elif booking_type_enum == BookingType.WEEK:
            # Weekly calculation: prefer L2 price, fallback to daily
            if "L2" in external_prices:
                l2_daily_rate = external_prices["L2"]
                total_cost = l2_daily_rate * total_days

                logger.debug(
                    f"ChildChair weekly (L2): {l2_daily_rate} × {total_days} = {total_cost}"
                )
            else:
                # Fallback to daily rate
                daily_price = offer_data.get("offerPrice", offer_data.get("price", 0))
                total_cost = daily_price * total_days

                logger.debug(
                    f"ChildChair weekly (fallback): {daily_price} × {total_days} = {total_cost}"
                )

        elif booking_type_enum == BookingType.MONTH:
            # Monthly calculation: prefer L3 price, fallback to daily
            if "L3" in external_prices:
                l3_daily_rate = external_prices["L3"]
                total_cost = l3_daily_rate * total_days

                logger.debug(
                    f"ChildChair monthly (L3): {l3_daily_rate} × {total_days} = {total_cost}"
                )
            else:
                # Fallback to daily rate
                daily_price = offer_data.get("offerPrice", offer_data.get("price", 0))
                total_cost = daily_price * total_days

                logger.debug(
                    f"ChildChair monthly (fallback): {daily_price} × {total_days} = {total_cost}"
                )
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

        return Money(total_cost, currency)

    def calculate_documents_offer_price(
        self,
        offer_data: Dict[str, Any],
        current_end_date: datetime,
        new_end_date: datetime,
        currency: str = "SAR",
    ) -> Money:
        """
        Calculate Documents offer price
        Documents are priced per month, calculated based on extension period
        """
        # Calculate months between current end date and new end date
        time_diff = new_end_date - current_end_date
        extension_days = time_diff.days
        months_to_add = max(1, (extension_days + 29) // 30)  # Round up to nearest month

        # Documents pricing is per month
        monthly_price = offer_data.get("offerPrice", offer_data.get("price", 0))
        total_cost = monthly_price * months_to_add

        logger.debug(
            f"Documents calculation: {monthly_price} × {months_to_add} months = {total_cost}"
        )

        return Money(total_cost, currency)

    def calculate_documents_offer_price_for_booking(
        self,
        offer_data: Dict[str, Any],
        booking_type: str,
        units: int,
        currency: str = "SAR",
    ) -> Money:
        """
        Calculate Documents offer price for new bookings
        Documents are always charged per month
        """
        booking_type_enum = BookingType(booking_type)
        monthly_price = offer_data.get("offerPrice", offer_data.get("price", 0))

        if booking_type_enum == BookingType.DAY:
            # For daily bookings, calculate months needed
            total_days = units
            months_needed = max(1, (total_days + 29) // 30)  # Round up to nearest month
            total_cost = monthly_price * months_needed
        elif booking_type_enum == BookingType.WEEK:
            # For weekly bookings, calculate months needed
            total_days = units * self.DAYS_PER_WEEK
            months_needed = max(1, (total_days + 29) // 30)  # Round up to nearest month
            total_cost = monthly_price * months_needed
        elif booking_type_enum == BookingType.MONTH:
            # For monthly bookings, charge per month
            months_needed = units
            total_cost = monthly_price * units
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

        logger.debug(
            f"Documents booking calculation: {monthly_price} × {months_needed} months = {total_cost}"
        )

        return Money(total_cost, currency)

    def calculate_offer_price(
        self,
        offer_data: Dict[str, Any],
        car_data: Dict[str, Any],
        booking_type: str,
        units: int,
        currency: str = "SAR",
        current_end_date: Optional[datetime] = None,
        new_end_date: Optional[datetime] = None,
        has_discount: bool = False,
        discount_percent: float = 0.0,
    ) -> Money:
        """
        Calculate price for any offer type
        Central method that delegates to specific calculation methods
        """
        offer_type = offer_data.get("offerType", offer_data.get("type", ""))

        try:
            offer_type_enum = OfferType(offer_type)
        except ValueError:
            raise ValidationError(f"Unsupported offer type: {offer_type}")

        # Calculate current car price (with discount if applicable)
        current_car_price = self.calculate_current_car_price(
            car_data, booking_type, has_discount, discount_percent
        )

        total_days = self.calculate_total_days(booking_type, units)

        if offer_type_enum == OfferType.INSURANCE:
            return self.calculate_insurance_offer_price(
                current_car_price, units, currency
            )

        elif offer_type_enum == OfferType.KM:
            return self.calculate_km_offer_price(current_car_price, units, currency)

        elif offer_type_enum == OfferType.CHILD_CHAIR:
            return self.calculate_child_chair_offer_price(
                offer_data, booking_type, units, total_days, currency
            )

        elif offer_type_enum == OfferType.DOCUMENTS:
            # For new bookings (no contract dates), use booking-specific calculation
            if not current_end_date or not new_end_date:
                return self.calculate_documents_offer_price_for_booking(
                    offer_data, booking_type, units, currency
                )
            # For contract extensions, use date-based calculation
            return self.calculate_documents_offer_price(
                offer_data, current_end_date, new_end_date, currency
            )
        else:
            raise ValidationError(
                f"Calculation not implemented for offer type: {offer_type}"
            )

    def calculate_extension_cost(
        self,
        car_data: Dict[str, Any],
        booking_type: str,
        units: int,
        currency: str = "SAR",
        has_discount: bool = False,
        discount_percent: float = 0.0,
        is_custom_rate: bool = False,
        custom_rate: Optional[float] = None,
    ) -> Money:
        """
        Calculate base extension cost for contract extension
        """
        if is_custom_rate and custom_rate is not None:
            if custom_rate <= 0:
                raise ValidationError("Custom rate must be positive")
            rate = custom_rate
        else:
            rate = self.calculate_current_car_price(
                car_data, booking_type, has_discount, discount_percent
            )

        extension_cost = rate * units

        logger.debug(f"Extension cost calculation: {rate} × {units} = {extension_cost}")

        return Money(extension_cost, currency)

    def calculate_total_extension_cost(
        self,
        car_data: Dict[str, Any],
        booking_type: str,
        units: int,
        offers: List[Dict[str, Any]] = None,
        currency: str = "SAR",
        current_end_date: Optional[datetime] = None,
        new_end_date: Optional[datetime] = None,
        has_discount: bool = False,
        discount_percent: float = 0.0,
        is_custom_rate: bool = False,
        custom_rate: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Calculate complete extension cost breakdown including all offers
        Returns detailed breakdown for transparency
        """
        # Calculate base extension cost
        extension_cost = self.calculate_extension_cost(
            car_data,
            booking_type,
            units,
            currency,
            has_discount,
            discount_percent,
            is_custom_rate,
            custom_rate,
        )

        # Calculate offers total
        total_offers_cost = Money(0, currency)
        offer_breakdown = []

        if offers:
            for offer in offers:
                try:
                    offer_cost = self.calculate_offer_price(
                        offer,
                        car_data,
                        booking_type,
                        units,
                        currency,
                        current_end_date,
                        new_end_date,
                        has_discount,
                        discount_percent,
                    )
                    total_offers_cost = total_offers_cost.add(offer_cost)
                    offer_breakdown.append(
                        {
                            "name": offer.get("offer", offer.get("name", "Unknown")),
                            "type": offer.get(
                                "offerType", offer.get("type", "Unknown")
                            ),
                            "cost": offer_cost.amount,
                        }
                    )
                except Exception as e:
                    logger.warning(f"Failed to calculate price for offer {offer}: {e}")
                    # Continue with other offers instead of failing completely
                    continue

        # Calculate subtotal
        subtotal = extension_cost.add(total_offers_cost)

        # Calculate taxes (15%)
        taxes = subtotal.multiply(self.TAX_RATE)

        # Calculate total with taxes
        total_cost = subtotal.add(taxes)

        return {
            "extension_cost": extension_cost.amount,
            "offers_total": total_offers_cost.amount,
            "offer_breakdown": offer_breakdown,
            "subtotal": subtotal.amount,
            "taxes": taxes.amount,
            "total_cost": total_cost.amount,
            "currency": currency,
            "calculation_details": {
                "booking_type": booking_type,
                "units": units,
                "total_days": self.calculate_total_days(booking_type, units),
                "current_car_price": (
                    self.calculate_current_car_price(
                        car_data, booking_type, has_discount, discount_percent
                    )
                    if not is_custom_rate
                    else custom_rate
                ),
                "has_discount": has_discount,
                "discount_percent": discount_percent,
                "tax_rate": self.TAX_RATE,
            },
        }
