"""
Wallet domain service for handling wallet operations and business logic
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from ...infrastructure.firebase_collections import get_firebase_db
from ..value_objects.money import Money


class WalletService:
    """Domain service for wallet operations"""

    def __init__(self):
        self.currency = "SAR"

    def get_wallet_balance(self, user_id: str) -> Money:
        """Get current wallet balance for a user"""
        try:
            db = get_firebase_db()
            if not db:
                return Money(Decimal("0"), self.currency)

            user_doc = db.collection("users").document(user_id).get()
            if user_doc.exists:
                data = user_doc.to_dict()
                balance = data.get("Wallet_Balance", 0.0)
                currency = data.get("Currency", self.currency)
                return Money(Decimal(str(balance)), currency)
            else:
                return Money(Decimal("0"), self.currency)
        except Exception as e:
            print(f"❌ Error getting wallet balance: {e}")
            return Money(Decimal("0"), self.currency)

    def add_money_to_wallet(
        self,
        user_id: str,
        amount: Money,
        reason: str,
        admin_user_id: Optional[str] = None,
        related_booking_id: Optional[str] = None,
        related_contract_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Add money to user's wallet"""
        try:
            db = get_firebase_db()
            if not db:
                return {"success": False, "error": "Database connection failed"}

            # Start a transaction
            transaction_ref = db.transaction()

            def add_money_transaction(transaction):
                user_ref = db.collection("users").document(user_id)
                user_doc = transaction.get(user_ref)

                if not user_doc.exists:
                    raise Exception(f"User {user_id} not found")

                user_data = user_doc.to_dict()
                current_balance = Decimal(str(user_data.get("Wallet_Balance", 0.0)))
                new_balance = current_balance + amount.amount

                # Update wallet balance
                transaction.update(user_ref, {"Wallet_Balance": float(new_balance)})

                # Add transaction record
                transaction_data = {
                    "action": "add",
                    "amount": float(amount.amount),
                    "reason": reason,
                    "adminUserId": admin_user_id or "system",
                    "timestamp": datetime.now(),
                    "previousBalance": float(current_balance),
                    "newBalance": float(new_balance),
                    "currency": amount.currency,
                    "relatedBookingId": related_booking_id,
                    "relatedContractId": related_contract_id,
                }

                transaction_doc_ref = user_ref.collection(
                    "Transaction_history"
                ).document()
                transaction.set(transaction_doc_ref, transaction_data)

                return {
                    "previousBalance": float(current_balance),
                    "newBalance": float(new_balance),
                    "transactionId": transaction_doc_ref.id,
                }

            result = transaction_ref.transaction(add_money_transaction)

            return {
                "success": True,
                "message": f"Added {amount} to wallet",
                "wallet": {
                    "previousBalance": result["previousBalance"],
                    "newBalance": result["newBalance"],
                    "currency": amount.currency,
                },
                "transactionId": result["transactionId"],
            }

        except Exception as e:
            print(f"❌ Error adding money to wallet: {e}")
            return {"success": False, "error": str(e)}

    def deduct_money_from_wallet(
        self,
        user_id: str,
        amount: Money,
        reason: str,
        admin_user_id: Optional[str] = None,
        related_booking_id: Optional[str] = None,
        related_contract_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Deduct money from user's wallet"""
        try:
            db = get_firebase_db()
            if not db:
                return {"success": False, "error": "Database connection failed"}

            # Start a transaction
            transaction_ref = db.transaction()

            def deduct_money_transaction(transaction):
                user_ref = db.collection("users").document(user_id)
                user_doc = transaction.get(user_ref)

                if not user_doc.exists:
                    raise Exception(f"User {user_id} not found")

                user_data = user_doc.to_dict()
                current_balance = Decimal(str(user_data.get("Wallet_Balance", 0.0)))

                # Check sufficient balance
                if current_balance < amount.amount:
                    raise Exception(
                        f"Insufficient balance. Current: {current_balance}, Requested: {amount.amount}"
                    )

                new_balance = current_balance - amount.amount

                # Update wallet balance
                transaction.update(user_ref, {"Wallet_Balance": float(new_balance)})

                # Add transaction record
                transaction_data = {
                    "action": "deduct",
                    "amount": float(amount.amount),
                    "reason": reason,
                    "adminUserId": admin_user_id or "system",
                    "timestamp": datetime.now(),
                    "previousBalance": float(current_balance),
                    "newBalance": float(new_balance),
                    "currency": amount.currency,
                    "relatedBookingId": related_booking_id,
                    "relatedContractId": related_contract_id,
                }

                transaction_doc_ref = user_ref.collection(
                    "Transaction_history"
                ).document()
                transaction.set(transaction_doc_ref, transaction_data)

                return {
                    "previousBalance": float(current_balance),
                    "newBalance": float(new_balance),
                    "transactionId": transaction_doc_ref.id,
                }

            result = transaction_ref.transaction(deduct_money_transaction)

            return {
                "success": True,
                "message": f"Deducted {amount} from wallet",
                "wallet": {
                    "previousBalance": result["previousBalance"],
                    "newBalance": result["newBalance"],
                    "currency": amount.currency,
                },
                "transactionId": result["transactionId"],
            }

        except Exception as e:
            print(f"❌ Error deducting money from wallet: {e}")
            return {"success": False, "error": str(e)}

    def process_refund(
        self,
        user_id: str,
        refund_amount: Money,
        reason: str,
        related_booking_id: Optional[str] = None,
        related_contract_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Process a refund to user's wallet (special case of add money)"""
        return self.add_money_to_wallet(
            user_id=user_id,
            amount=refund_amount,
            reason=f"Refund: {reason}",
            admin_user_id="system-refund",
            related_booking_id=related_booking_id,
            related_contract_id=related_contract_id,
        )

    def get_transaction_history(
        self,
        user_id: str,
        limit: int = 50,
        start_after: Optional[str] = None,
        action_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get user's transaction history"""
        try:
            db = get_firebase_db()
            if not db:
                return {"success": False, "error": "Database connection failed"}

            # Build query
            query = (
                db.collection("users")
                .document(user_id)
                .collection("Transaction_history")
            )
            query = query.order_by("timestamp", direction="DESCENDING")

            if action_filter:
                query = query.where("action", "==", action_filter)

            if start_after:
                # Get the document to start after
                start_doc = (
                    db.collection("users")
                    .document(user_id)
                    .collection("Transaction_history")
                    .document(start_after)
                    .get()
                )
                if start_doc.exists:
                    query = query.start_after(start_doc)

            query = query.limit(limit + 1)  # Get one extra to check if there are more

            docs = query.get()
            transactions = []

            for i, doc in enumerate(docs):
                if i >= limit:  # Don't include the extra document in results
                    break

                data = doc.to_dict()
                transaction_data = {
                    "id": doc.id,
                    "action": data.get("action"),
                    "amount": data.get("amount"),
                    "reason": data.get("reason"),
                    "adminUserId": data.get("adminUserId"),
                    "timestamp": (
                        data.get("timestamp").isoformat()
                        if data.get("timestamp")
                        else None
                    ),
                    "previousBalance": data.get("previousBalance"),
                    "newBalance": data.get("newBalance"),
                    "currency": data.get("currency", self.currency),
                    "relatedBookingId": data.get("relatedBookingId"),
                    "relatedContractId": data.get("relatedContractId"),
                }
                transactions.append(transaction_data)

            has_more = len(docs) > limit

            return {
                "success": True,
                "transactions": transactions,
                "hasMore": has_more,
                "totalCount": len(transactions),
            }

        except Exception as e:
            print(f"❌ Error getting transaction history: {e}")
            return {
                "success": False,
                "error": str(e),
                "transactions": [],
                "hasMore": False,
                "totalCount": 0,
            }

    def calculate_refund_with_tax(
        self, subtotal: Decimal, tax_rate: Decimal = Decimal("0.15")
    ) -> Dict[str, Money]:
        """Calculate refund amounts including tax breakdown"""
        tax_amount = subtotal * tax_rate
        total_refund = subtotal + tax_amount

        return {
            "subtotal": Money(subtotal, self.currency),
            "tax": Money(tax_amount, self.currency),
            "total": Money(total_refund, self.currency),
        }

    def validate_wallet_operation(
        self, user_id: str, operation_amount: Money, operation_type: str
    ) -> Dict[str, Any]:
        """Validate if a wallet operation can be performed"""
        current_balance = self.get_wallet_balance(user_id)

        if (
            operation_type == "deduct"
            and current_balance.amount < operation_amount.amount
        ):
            return {
                "valid": False,
                "error": f"Insufficient balance. Current: {current_balance}, Required: {operation_amount}",
                "currentBalance": current_balance,
            }

        if operation_amount.amount <= 0:
            return {
                "valid": False,
                "error": "Operation amount must be positive",
                "currentBalance": current_balance,
            }

        return {"valid": True, "currentBalance": current_balance}
