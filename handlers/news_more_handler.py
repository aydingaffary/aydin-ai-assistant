
"""News more handler."""

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.news_handler import build_news_message, news_keyboard
from services.chat_state import get_member_state
from services.news_service import NewsService

news_service = NewsService()


async def handle_news_more(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show the next page of news for the requesting member."""

    query = update.callback_query
    if query is None:
        return

    chat = update.effective_chat
    user = update.effective_user

    is_group = (
        chat is not None
        and chat.type in ("group", "supergroup")
    )

    # Group buttons belong to the member who requested the news.
    if is_group:
        expected_data = f"news_more_{user.id}" if user else ""
        if query.data != expected_data:
            await query.answer(
                "این دکمه متعلق به عضو دیگری است؛ از منوی اخبار خودت استفاده کن.",
                show_alert=True,
            )
            return

    await query.answer()

    state = get_member_state(update, context)
    topic = state.get("last_news_topic", "")
    offset = state.get("news_offset", 3)

    news = news_service.get_news(topic, limit=3, offset=offset)

    if not news:
        await query.answer(
            "خبر بیشتری پیدا نشد.",
            show_alert=True,
        )
        return

    response = build_news_message(news, start=offset + 1)
    displayed_count = response.count("<a href=")

    if displayed_count == 0:
        await query.answer(
            "خبر قابل نمایش دیگری پیدا نشد.",
            show_alert=True,
        )
        return

    next_offset = offset + displayed_count
    owner_id = user.id if is_group and user else None

    try:
        await query.edit_message_text(
            response,
            parse_mode=ParseMode.HTML,
            reply_markup=news_keyboard(owner_id),
            disable_web_page_preview=True,
        )
    except Exception as exc:
        if "Message is not modified" not in str(exc):
            raise

    state["news_offset"] = next_offset
