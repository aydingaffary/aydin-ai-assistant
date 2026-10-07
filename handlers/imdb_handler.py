"""IMDb handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.release_service import ReleaseService


async def handle_imdb(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Ask user for movie title."""

    context.user_data["waiting_movie"] = True

    await update.message.reply_text("🎬 نام فیلم یا سریال را وارد کنید:")


async def handle_movie_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Search movie from OMDb."""

    title = update.message.text.strip()

    service = ReleaseService()

    movie = service.get_movie(title)

    context.user_data["waiting_movie"] = False

    if not movie:
        await update.message.reply_text("❌ فیلم پیدا نشد.")
        return

    text = (
        f"🎬 {movie['title']} ({movie['year']})\n\n"
        f"⭐ IMDb: {movie['imdb_rating']}\n"
        f"🎭 ژانر: {movie['genre']}\n"
        f"🎬 کارگردان: {movie['director']}\n"
        f"👥 بازیگران: {movie['actors']}\n\n"
        f"📝 خلاصه:\n{movie['plot']}"
    )

    if movie["poster"] and movie["poster"] != "N/A":
        await update.message.reply_photo(
            photo=movie["poster"],
            caption=text[:1024],
        )
    else:
        await update.message.reply_text(text)
