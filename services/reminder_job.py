"""Reminder background job."""

from datetime import datetime

from services.reminder_service import ReminderService


service = ReminderService()


async def check_reminders(context):
    """Check reminders and send notifications."""

    now = datetime.now().strftime("%H:%M")

    reminders = service.load()

    remaining = []

    for reminder in reminders:

        if reminder["time"] == now:

            await context.bot.send_message(
                chat_id=reminder["user_id"],
                text=(
                    "🔔 یادآوری شما:\n\n"
                    f"📝 {reminder['text']}"
                ),
            )

        else:
            remaining.append(reminder)


    service.save(remaining)