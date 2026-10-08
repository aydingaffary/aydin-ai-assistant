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

    def get_payment(
        self,
        payment_id: int,
    ):
        """Get payment by ID."""

        with get_connection() as connection:
            return connection.execute(
                """
                SELECT
                    id,
                    user_id,
                    plan,
                    amount,
                    status,
                    created_at
                FROM payments
                WHERE id = ?
                """,
                (payment_id,),
            ).fetchone()


    def approve_payment(
        self,
        payment_id: int,
    ) -> bool:
        """Approve payment and activate user premium."""

        payment = self.get_payment(payment_id)

        if not payment:
            return False

        user_id = payment[1]

        with get_connection() as connection:

            connection.execute(
                """
                UPDATE payments
                SET status = ?
                WHERE id = ?
                """,
                (
                    "paid",
                    payment_id,
                ),
            )

            connection.execute(
                """
                UPDATE users
                SET is_premium = 1
                WHERE user_id = ?
                """,
                (user_id,),
            )

        return True