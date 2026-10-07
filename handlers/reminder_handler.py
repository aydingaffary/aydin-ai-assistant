"""Reminder handler."""

from datetime import datetime

from services.reminder_service import ReminderService


service = ReminderService()


async def handle_reminder(update, context):
    """Handle reminder creation."""

    text = update.message.text

    step = context.user_data.get("reminder_step")


    if step == "text":
        context.user_data["reminder_text"] = text
        context.user_data["reminder_step"] = "time"

        await update.message.reply_text(
            "⏰ ساعت یادآوری را وارد کنید.\n\n"
            "مثال:\n"
            "11:00"
        )
        return


    if step == "time":
        reminder_text = context.user_data.get(
            "reminder_text"
        )

        try:
            datetime.strptime(text, "%H:%M")

        except ValueError:
            await update.message.reply_text(
                "❌ ساعت اشتباه است.\n"
                "مثال درست: 11:00"
            )
            return


        service.add(
            user_id=update.effective_user.id,
            text=reminder_text,
            time=text,
        )


        context.user_data.clear()


        await update.message.reply_text(
            "✅ یادآوری ثبت شد.\n\n"
            f"🔔 ساعت: {text}\n"
            f"📝 کار: {reminder_text}"
        )