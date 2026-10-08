"""Payment service."""

from datetime import datetime

from database.db import get_connection


class PaymentService:
    """Handle subscription payments."""

    def create_payment(
        self,
        user_id: int,
        plan: str,
        amount: int,
    ) -> None:
        """Create pending payment."""

        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO payments (
                    user_id,
                    plan,
                    amount,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    plan,
                    amount,
                    "pending",
                    datetime.now().isoformat(),
                ),
            )