from models.user import User


class UserService:
    """Manage application users."""

    def __init__(self) -> None:
        self.users: dict[int, User] = {}

    def get_or_create_user(
        self,
        user_id: int,
        username: str | None = None,
    ) -> User:
        """Return existing user or create a new one."""

        if user_id not in self.users:
            self.users[user_id] = User(
                user_id=user_id,
                username=username,
            )

        return self.users[user_id]

    def get_user(self, user_id: int) -> User | None:
        """Get user by id."""

        return self.users.get(user_id)