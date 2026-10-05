"""Usage limiter service."""

from datetime import datetime
from services.user_service import UserService
from database.db import get_connection
from services.subscription_service import SubscriptionService

class AIUsageService:
    """Manage AI request limits."""

    LIMITS = {
        "smart_assistant": 10,
        "news": 1,
    }

    def __init__(self):
        self.subscription_service = SubscriptionService()

    def can_use_ai(
        self,
        user_id: int,
        feature: str,
    ) -> bool:
        """Check if user can use a feature."""
        if self.subscription_service.has_access(user_id):
            return True

        connection = get_connection()
        cursor = connection.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (user_id, feature, today),
        )

        result = cursor.fetchone()

        connection.close()

        if not result:
            return True

        return result[0] < self.LIMITS.get(feature, 0)

    def consume_ai(
        self,
        user_id: int,
        feature: str,
    ) -> None:
        """Register usage."""
        
        if self.subscription_service.has_access(user_id):
            return

        connection = get_connection()
        cursor = connection.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (user_id, feature, today),
        )

        result = cursor.fetchone()

        if result:
            cursor.execute(
                """
                UPDATE ai_usage
                SET count = count + 1
                WHERE user_id = ?
                AND feature = ?
                AND usage_date = ?
                """,
                (user_id, feature, today),
            )
        else:
            cursor.execute(
                """
                INSERT INTO ai_usage
                (user_id, feature, usage_date, count)
                VALUES (?, ?, ?, 1)
                """,
                (user_id, feature, today),
            )

        connection.commit()
        connection.close()

    def remaining(
        self,
        user_id: int,
        feature: str,
    ) -> int:
        """Return remaining free usage."""

        if self.user_service.is_premium(user_id):
            return -1

        connection = get_connection()
        cursor = connection.cursor()

        today = datetime.now().strftime("%Y-%m-%d")

        cursor.execute(
            """
            SELECT count
            FROM ai_usage
            WHERE user_id = ?
            AND feature = ?
            AND usage_date = ?
            """,
            (user_id, feature, today),
        )

        result = cursor.fetchone()

        connection.close()

        used = result[0] if result else 0

        limit = self.LIMITS.get(feature, 0)

        return max(limit - used, 0)