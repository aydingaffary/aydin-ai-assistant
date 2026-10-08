"""Payment service."""

from datetime import datetime

from dateutil.relativedelta import relativedelta

from database.db import get_connection


class PaymentService:
    """Handle subscription payments."""

    ALLOWED_PLANS = {
        "اشتراک یک ماهه",
        "اشتراک سه ماهه",
    }

    def create_payment(
        self,
        user_id: int,
        plan: str,
        amount: int,
    ) -> None:
        """Create pending payment."""

        if user_id <= 0:
            raise ValueError("Invalid user_id.")

        if plan not in self.ALLOWED_PLANS:
            raise ValueError("Invalid subscription plan.")

        if amount <= 0:
            raise ValueError("Invalid payment amount.")

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

        if payment_id <= 0:
            return None

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

        if payment_id <= 0:
            return False

        with get_connection() as connection:

            payment = connection.execute(
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

            if not payment:
                return False

            if payment[4] != "pending":
                return False

            user_id = payment[1]
            plan = payment[2]

            if user_id <= 0:
                return False

            if plan not in self.ALLOWED_PLANS:
                return False

            user = connection.execute(
                """
                SELECT premium_until
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            if not user:
                return False

            current_until = user[0]
            now = datetime.now()

            if current_until:
                try:
                    base_date = datetime.fromisoformat(current_until)
                except ValueError:
                    base_date = now

                if base_date < now:
                    base_date = now
            else:
                base_date = now

            if plan == "اشتراک یک ماهه":
                premium_until = base_date + relativedelta(months=1)

            elif plan == "اشتراک سه ماهه":
                premium_until = base_date + relativedelta(months=3)

            else:
                return False

            result = connection.execute(
                """
                UPDATE payments
                SET status = ?
                WHERE id = ?
                  AND status = ?
                """,
                (
                    "paid",
                    payment_id,
                    "pending",
                ),
            )

            if result.rowcount != 1:
                return False

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