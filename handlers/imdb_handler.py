"""IMDb handler."""

from services.release_service import ReleaseService
from services.chat_state import get_member_state


async def handle_imdb(update, context):
    state = get_member_state(update, context)
    state["waiting_movie"] = True
    await update.message.reply_text("🎬 نام فیلم یا سریال را وارد کنید:")


async def handle_movie_search(update, context):
    title = update.message.text.strip()
    state = get_member_state(update, context)
    state.pop("waiting_movie", None)

    service = ReleaseService()
    movie = service.get_movie(title)

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

    if movie.get("poster") and movie["poster"] != "N/A":
        await update.message.reply_photo(
            photo=movie["poster"],
            caption=text[:1024],
        )
    else:
        await update.message.reply_text(text)
