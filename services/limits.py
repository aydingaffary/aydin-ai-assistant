from datetime import date


class UserLimitManager:
    """Manage free and paid user request limits."""

    FREE_LIMIT = 10

    def __init__(self) -> None:
        self.users = {}

    def can_use_ai(self, user_id: int) -> bool:
        """Check if user can send an AI request."""

        today = date.today()

        user = self.users.get(user_id)

        if not user:
            self.users[user_id] = {
                "date": today,
                "count": 0,
                "premium": False,
            }
            return True

        if user["date"] != today:
            user["date"] = today
            user["count"] = 0

        if user["premium"]:
            return True

        return user["count"] < self.FREE_LIMIT

    def record_request(self, user_id: int) -> None:
        """Increase user's AI request count."""

        if user_id in self.users:
            self.users[user_id]["count"] += 1

    def remaining_requests(self, user_id: int) -> int:
        """Return remaining free requests."""

        user = self.users.get(user_id)

        if not user or user["premium"]:
            return -1

        return self.FREE_LIMIT - user["count"]

    def set_premium(self, user_id: int) -> None:
        """Upgrade user to premium."""

        if user_id not in self.users:
            self.users[user_id] = {
                "date": date.today(),
                "count": 0,
                "premium": True,
            }
        else:
            self.users[user_id]["premium"] = True
