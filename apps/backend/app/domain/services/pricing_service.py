"""
Pricing domain service - Encapsulates complex pricing business logic
"""

from datetime import datetime
from typing import Any, Dict, List

from ..base import ValidationError
from ..entities.contract import Contract
from ..value_objects.money import Money


class PricingService:
    """Domain service for pricing calculations"""

    TAX_RATE = 0.15  # 15% tax rate

    def calculate_base_price(
        self, car_data: Dict[str, Any], booking_type: str, count: int
    ) -> Money:
        """Calculate base rental price"""
        if booking_type == "Day":
            daily_rate = car_data.get(
                "rental_price_day", car_data.get("rental_price", 0)
            )
            base_amount = daily_rate * count
        elif booking_type == "Week":
            weekly_rate = car_data.get("rental_price_week", 0)
            if weekly_rate == 0:
                # Fallback to daily rate * 7
                daily_rate = car_data.get(
                    "rental_price_day", car_data.get("rental_price", 0)
                )
                weekly_rate = daily_rate * 7
            base_amount = weekly_rate * count
        elif booking_type == "Month":
            monthly_rate = car_data.get(
                "rental_price_month", car_data.get("rental_price_mounth", 0)
            )
            if monthly_rate == 0:
                # Fallback to daily rate * 30
                daily_rate = car_data.get(
                    "rental_price_day", car_data.get("rental_price", 0)
                )
                monthly_rate = daily_rate * 30
            base_amount = monthly_rate * count
        else:
            raise ValidationError(f"Invalid booking type: {booking_type}")

        currency = car_data.get("Currency", "SAR")
        return Money(base_amount, currency)

    def calculate_package_price(
        self, car_data: Dict[str, Any], package_months: int
    ) -> Money:
        """Calculate package booking price"""
        packages = car_data.get("Packages", [])

        for package in packages:
            if package.get("packageMonths") == package_months:
                price = package.get("priceB4Discount", 0)
                currency = car_data.get("Currency", "SAR")
                return Money(price, currency)

        raise ValidationError(f"Package for {package_months} months not found")

    def apply_discount(self, base_price: Money, discount_percent: float) -> Money:
        """Apply discount to base price"""
        if discount_percent < 0 or discount_percent > 100:
            raise ValidationError("Discount percent must be between 0 and 100")

        return base_price.apply_discount(discount_percent)

    def calculate_taxes(self, taxable_amount: Money) -> Money:
        """Calculate taxes on taxable amount"""
        return taxable_amount.calculate_tax(self.TAX_RATE)

    def calculate_offers_total(
        self, offers: List[Dict[str, Any]], base_price: Money
    ) -> Money:
        """Calculate total cost of selected offers"""
        total = Money(0, base_price.currency)

        for offer in offers:
            offer_price = self._calculate_offer_price(offer, base_price)
            total = total.add(offer_price)

        return total

    def _calculate_offer_price(self, offer: Dict[str, Any], base_price: Money) -> Money:
        """Calculate price for a single offer"""
        offer_type = offer.get("type", "").lower()

        if offer_type == "km_package":
            # KM Package is 25% of base price
            return base_price.multiply(0.25)
        elif offer_type == "insurance":
            # Insurance is a percentage of base price
            percentage = offer.get("percentage", 0)
            return base_price.multiply(percentage / 100)
        elif offer_type == "documents":
            # Documents is a fixed price
            fixed_price = offer.get("price", 0)
            return Money(fixed_price, base_price.currency)
        elif offer_type == "child_chair":
            # Child chair has daily rates
            daily_rate = offer.get("daily_rate", 0)
            days = offer.get("days", 1)
            return Money(daily_rate * days, base_price.currency)
        else:
            # Unknown offer type - use fixed price if available
            fixed_price = offer.get("price", 0)
            return Money(fixed_price, base_price.currency)

    def calculate_total_booking_cost(
        self,
        car_data: Dict[str, Any],
        booking_type: str,
        count: int,
        discount_percent: float = 0,
        delivery_fee: float = 0,
        offers: List[Dict[str, Any]] = None,
        is_package_booking: bool = False,
        package_months: int = None,
    ) -> Dict[str, Money]:
        """Calculate complete booking cost breakdown"""

        currency = car_data.get("Currency", "SAR")

        # Calculate base price
        if is_package_booking and package_months:
            booking_cost = self.calculate_package_price(car_data, package_months)
        else:
            booking_cost = self.calculate_base_price(car_data, booking_type, count)

        # Apply discount
        if discount_percent > 0:
            booking_cost = self.apply_discount(booking_cost, discount_percent)

        # Calculate offers
        offers_total = Money(0, currency)
        if offers:
            offers_total = self.calculate_offers_total(offers, booking_cost)

        # Calculate taxes (on booking cost only, not on offers)
        taxes = self.calculate_taxes(booking_cost)

        # Delivery fee
        delivery = Money(delivery_fee, currency)

        # Total cost
        total_cost = booking_cost.add(taxes).add(delivery).add(offers_total)

        return {
            "booking_cost": booking_cost,
            "taxes": taxes,
            "delivery_fee": delivery,
            "offers_total": offers_total,
            "total_cost": total_cost,
        }

    def calculate_extension_cost(
        self,
        contract: Contract,
        new_end_date: datetime,
        car_data: Dict[str, Any] = None,
    ) -> Money:
        """Calculate cost for contract extension"""
        if new_end_date <= contract.date_range.end_date:
            raise ValidationError("Extension date must be after current end date")

        # Calculate extension period
        extension_days = (new_end_date - contract.date_range.end_date).days

        # Determine extension pricing based on original booking type
        if contract.booking_type == "Day":
            daily_rate = (
                contract.booking_cost.amount / contract.date_range.duration_days
            )
            extension_cost = Money(
                daily_rate * extension_days, contract.booking_cost.currency
            )
        elif contract.booking_type == "Week":
            # If less than a week, use daily rate
            if extension_days < 7:
                daily_rate = (
                    contract.booking_cost.amount / contract.date_range.duration_days
                )
                extension_cost = Money(
                    daily_rate * extension_days, contract.booking_cost.currency
                )
            else:
                # Calculate weekly rate and pro-rate
                weekly_rate = (
                    contract.booking_cost.amount / contract.date_range.duration_weeks
                )
                extension_cost = Money(
                    weekly_rate * (extension_days / 7), contract.booking_cost.currency
                )
        elif contract.booking_type == "Month":
            # If less than a month, use daily rate
            if extension_days < 30:
                daily_rate = (
                    contract.booking_cost.amount / contract.date_range.duration_days
                )
                extension_cost = Money(
                    daily_rate * extension_days, contract.booking_cost.currency
                )
            else:
                # Calculate monthly rate and pro-rate
                monthly_rate = (
                    contract.booking_cost.amount / contract.date_range.duration_months
                )
                extension_cost = Money(
                    monthly_rate * (extension_days / 30), contract.booking_cost.currency
                )
        else:
            raise ValidationError(f"Unknown booking type: {contract.booking_type}")

        # Add taxes on extension
        extension_taxes = self.calculate_taxes(extension_cost)
        total_extension_cost = extension_cost.add(extension_taxes)

        return total_extension_cost

    def validate_pricing_data(self, car_data: Dict[str, Any]) -> None:
        """Validate that car has required pricing data"""
        required_fields = ["rental_price_day", "rental_price"]

        if not any(field in car_data for field in required_fields):
            raise ValidationError(
                "Car must have at least rental_price_day or rental_price"
            )

        # Validate that prices are positive
        for field in [
            "rental_price_day",
            "rental_price_week",
            "rental_price_month",
            "rental_price",
        ]:
            if field in car_data and car_data[field] < 0:
                raise ValidationError(f"Car {field} cannot be negative")
