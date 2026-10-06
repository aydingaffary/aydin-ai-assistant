"""Subscription management service."""

from services.user_service import UserService


class SubscriptionService:
    """Manage user subscription access."""

    def __init__(self) -> None:
        self.user_service = UserService()

    def has_access(self, user_id: int) -> bool:
        """Return True if user has premium access."""

        return self.user_service.is_premium(user_id)
