"""Reminder handler."""

from telegram import Update
from telegram.ext import ContextTypes

from datetime import datetime


async def handle_reminder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Create reminder."""

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
                "❌ فرمت ساعت اشتباه است.\n"
                "مثال درست: 11:00"
            )
            return


        context.user_data.pop(
            "reminder_step",
            None
        )

        await update.message.reply_text(
            "✅ یادآوری ثبت شد.\n\n"
            f"🔔 زمان: {text}\n"
            f"📝 متن: {reminder_text}"
        )