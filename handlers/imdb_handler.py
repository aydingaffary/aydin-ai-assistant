"""IMDb handler."""

from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from services.release_service import ReleaseService
from services.date_service import format_jalali_date


async def handle_imdb(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show upcoming IMDb releases."""

    service = ReleaseService()

    releases = service.get_releases(
        start_date=date.today(),
        days=7,
    )

    if not releases:
        await update.message.reply_text("🎬 در ۷ روز آینده انتشار جدیدی پیدا نشد.")
        return

    text = "🎬 انتشارهای این هفته:\n\n"

    for item in releases[:10]:
        jalali_date = format_jalali_date(item["release_date"])

        text += (
            f"📅 {jalali_date}\n"
            f"{'📺' if item['type'] == 'tv' else '🎥'} "
            f"{item['title']}\n"
            f"🔗 {item['url']}\n\n"
        )

    await update.message.reply_text(text)
