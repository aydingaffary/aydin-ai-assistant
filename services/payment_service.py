"""Payment service."""

from datetime import datetime

from dateutil.relativedelta import relativedelta
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

        if payment[4] == "paid":
            return False

        user_id = payment[1]
        plan = payment[2]

        with get_connection() as connection:

            user = connection.execute(
                """
                SELECT premium_until
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            current_until = user[0] if user else None

            if current_until:
                base_date = datetime.fromisoformat(current_until)

                if base_date < datetime.now():
                    base_date = datetime.now()
            else:
                base_date = datetime.now()

            if plan == "اشتراک یک ماهه":
                premium_until = base_date + relativedelta(months=1)

            elif plan == "اشتراک سه ماهه":
                premium_until = base_date + relativedelta(months=3)

            else:
                return False

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
                SET is_premium = 1,
                    premium_until = ?
                WHERE user_id = ?
                """,
                (
                    premium_until.isoformat(),
                    user_id,
                ),
            )

        return True