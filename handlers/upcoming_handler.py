"""Upcoming movies handler."""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from services.upcoming_service import UpcomingService
from services.date_service import format_jalali_date


async def handle_upcoming(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show upcoming movies."""

    service = UpcomingService()

    movies = service.get_upcoming(
        days=30,
    )

    if not movies:
        await update.message.reply_text(
            "🎬 فعلاً اطلاعات اکران‌های پیش رو در دسترس نیست."
        )
        return

    text = "🎬 اکران‌های پیش رو:\n\n"

    for index, movie in enumerate(movies[:10], start=1):

        release_date = movie.get("date")

        if release_date:
            jalali_date = format_jalali_date(date.fromisoformat(release_date))
        else:
            jalali_date = "-"

        text += f"🎥 {index}. {movie['title']}\n" f"📅 تاریخ اکران: {jalali_date}\n"

        if movie.get("rating"):
            text += f"⭐ امتیاز: {movie['rating']}\n"

        if movie.get("imdb_url"):
            text += f"🔗 IMDb:\n{movie['imdb_url']}\n"

        text += "\n"
        text += "─" * 20
        text += "\n\n"

    await update.message.reply_text(text)
