"""Reminder service."""

from datetime import datetime


class ReminderService:
    """Manage user reminders."""

    def __init__(self):
        self.reminders = []

    def add_reminder(
        self,
        user_id: int,
        text: str,
        reminder_time: str,
    ):
        """Add new reminder."""

        self.reminders.append(
            {
                "user_id": user_id,
                "text": text,
                "time": reminder_time,
            }
        )

    def get_reminders(self):
        """Return reminders."""

        return self.reminders