from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    """Represent a Telegram user."""

    user_id: int
    username: str | None = None
    is_premium: bool = False
    created_at: datetime = field(default_factory=datetime.now)