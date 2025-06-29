"""
Installment Entity
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

# Simple dataclasses, no need for base Entity


@dataclass
class Transaction:
    """Payment transaction details"""

    id: str
    type: str  # CASH, WALLET, MOYSAR_PAYMENT
    status: str  # success, paid
    total_amount: float
    amount_paid_with_payment: float
    amount_paid_with_wallet: float
    payment_date: Optional[str] = None
    payment_method: Optional[str] = None
    source: Optional[str] = None
    payment_last4: Optional[str] = None
    moysar_payment_id: Optional[str] = None
    currency: Optional[str] = None
    moysar_fee: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "totalAmount": self.total_amount,
            "amountPaiedWithPayment": self.amount_paid_with_payment,
            "amountPaiedWithWallet": self.amount_paid_with_wallet,
        }

        # Add optional fields if present
        if self.payment_date:
            data["paymentDate"] = self.payment_date
        if self.payment_method:
            data["paymentMethod"] = self.payment_method
        if self.source:
            data["source"] = self.source
        if self.payment_last4:
            data["paymentLast4"] = self.payment_last4
        if self.moysar_payment_id:
            data["moysarPaymentId"] = self.moysar_payment_id
        if self.currency:
            data["currency"] = self.currency
        if self.moysar_fee is not None:
            data["moysarFee"] = self.moysar_fee

        return data


@dataclass
class Installment:
    """Installment entity for contracts and bookings"""

    id: str
    due_date: datetime
    formatted_due_date: str
    is_paid: bool
    amount: float
    payment_nr: int
    transaction: Optional[Transaction] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "dueDate": self.due_date,
            "formattedDueDate": self.formatted_due_date,
            "isPaid": self.is_paid,
            "amount": self.amount,
            "paymentNr": self.payment_nr,
        }

        if self.transaction:
            data["transaction"] = self.transaction.to_dict()

        return data

    def pay(self, transaction: Transaction) -> None:
        """Mark installment as paid with transaction details"""
        self.is_paid = True
        self.transaction = transaction

    @staticmethod
    def format_date(date: datetime) -> str:
        """Format date for display"""
        return date.strftime("%B %d, %Y")  # e.g., "January 26, 2025"
