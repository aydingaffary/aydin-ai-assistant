"""Upcoming TV handler."""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from services.upcoming_service import UpcomingService
from services.date_service import format_jalali_date


async def handle_tv_upcoming(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show upcoming TV series."""

    service = UpcomingService()

    series = service.get_tv(
        days=30,
    )

    if not series:
        await update.message.reply_text(
            "📺 فعلاً اطلاعات سریال‌های پیش رو در دسترس نیست."
        )
        return

    text = "📺 سریال‌های پیش رو:\n\n"

    for index, item in enumerate(series[:10], start=1):

        jalali_date = format_jalali_date(date.fromisoformat(item["date"]))

        text += f"📺 {index}. {item['title']}\n" f"📅 تاریخ پخش: {jalali_date}\n"

        if item.get("rating"):
            text += f"⭐ امتیاز: {item['rating']}\n"

        if item.get("imdb_url"):
            text += f"🔗 IMDb:\n{item['imdb_url']}\n"

        text += "\n"
        text += "─" * 20
        text += "\n\n"

    await update.message.reply_text(text)
