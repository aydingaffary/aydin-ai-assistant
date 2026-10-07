"""Reminder storage service."""

import json
from pathlib import Path

FILE_PATH = Path("data/reminders.json")


class ReminderService:
    """Manage reminders."""

    def load(self):
        """Load reminders."""

        if not FILE_PATH.exists():
            return []

        with open(
            FILE_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def save(self, reminders):
        """Save reminders."""

        FILE_PATH.parent.mkdir(exist_ok=True)

        with open(
            FILE_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                reminders,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def add(
        self,
        user_id: int,
        text: str,
        time: str,
    ):
        """Add reminder."""

        reminders = self.load()

        reminders.append(
            {
                "user_id": user_id,
                "text": text,
                "time": time,
            }
        )

        self.save(reminders)

        return True
