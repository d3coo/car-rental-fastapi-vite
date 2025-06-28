"""
Money value object for handling monetary values with currency
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass(frozen=True)
class Money:
    """Immutable value object representing money with currency"""
    amount: Decimal
    currency: str = "SAR"
    
    def __init__(self, amount: Union[int, float, str, Decimal], currency: str = "SAR"):
        # Ensure amount is stored as Decimal for precision
        if isinstance(amount, (int, float, str)):
            object.__setattr__(self, 'amount', Decimal(str(amount)))
        else:
            object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency.upper())
    
    def add(self, other: 'Money') -> 'Money':
        """Add two money values with same currency"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot add different currencies: {self.currency} and {other.currency}")
        return Money(self.amount + other.amount, self.currency)
    
    def subtract(self, other: 'Money') -> 'Money':
        """Subtract money value with same currency"""
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract different currencies: {self.currency} and {other.currency}")
        return Money(self.amount - other.amount, self.currency)
    
    def multiply(self, factor: Union[int, float, Decimal]) -> 'Money':
        """Multiply money by a factor"""
        return Money(self.amount * Decimal(str(factor)), self.currency)
    
    def apply_discount(self, discount_percent: Union[int, float]) -> 'Money':
        """Apply a percentage discount"""
        factor = 1 - (Decimal(str(discount_percent)) / 100)
        return self.multiply(factor)
    
    def calculate_tax(self, tax_rate: Union[int, float]) -> 'Money':
        """Calculate tax amount"""
        return self.multiply(Decimal(str(tax_rate)) / 100)
    
    def with_tax(self, tax_rate: Union[int, float]) -> 'Money':
        """Return total with tax included"""
        tax = self.calculate_tax(tax_rate)
        return self.add(tax)
    
    def to_float(self) -> float:
        """Convert to float for JSON serialization"""
        return float(self.amount)
    
    def __str__(self) -> str:
        return f"{self.currency} {self.amount:.2f}"
    
    def __repr__(self) -> str:
        return f"Money({self.amount}, '{self.currency}')"