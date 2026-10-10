
"""News handler."""

from html import escape

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from services.news_service import NewsService

news_service = NewsService()
MAX_MESSAGE_LENGTH = 3800


def format_news_item(index: int, item: dict) -> str:
    """Format one news item with a clickable title."""

    title = escape(item.get("title_fa") or item.get("title", "بدون عنوان"))
    summary = escape(
        (item.get("summary_fa") or item.get("summary", "")).strip()
    )
    source = escape(item.get("source", "منبع نامشخص"))
    link = escape(item.get("link", ""), quote=True)

    text = f'<b>{index}. <a href="{link}">{title}</a></b>\n'
    if summary:
        text += f"{summary}\n"
    text += f"<i>🌐 {source}</i>"

    return text


def build_news_message(news: list[dict], start: int = 1) -> str:
    """Build a Telegram-safe message within the character limit."""

    heading = "<b>📰 تازه‌ترین خبرها</b>\n\n"
    entries = []
    current_length = len(heading)

    for index, item in enumerate(news, start=start):
        entry = format_news_item(index, item)
        separator = "\n\n━━━━━━━━━━━━━━\n\n" if entries else ""

        if current_length + len(separator) + len(entry) > MAX_MESSAGE_LENGTH:
            break

        entries.append(entry)
        current_length += len(separator) + len(entry)

    return heading + "\n\n━━━━━━━━━━━━━━\n\n".join(entries)


def news_keyboard(user_id: int | None = None) -> InlineKeyboardMarkup:
    callback_data = (
        f"news_more_{user_id}" if user_id is not None else "news_more"
    )
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("📰 اخبار بیشتر", callback_data=callback_data)]]
    )


async def handle_news(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle news requests in private chats and groups."""

    if update.message is None:
        return

    from services.chat_state import get_member_state

    state = get_member_state(update, context)
    raw_topic = (update.message.text or "").strip()

    general_news_aliases = {
        "📰 اخبار",
        "اخبار",
        "خبرها",
        "آخرین اخبار",
        "اخبار روز",
    }
    topic = "" if raw_topic in general_news_aliases else raw_topic

    news = news_service.get_news(topic, limit=3, offset=0)

    if not news:
        state["last_news_topic"] = topic
        state["news_offset"] = 0
        await update.message.reply_text(
            f"❌ خبری درباره «{escape(topic or 'عمومی')}» پیدا نشد."
        )
        return

    message = build_news_message(news)
    displayed_count = message.count("<a href=")

    state["last_news_topic"] = topic
    state["news_offset"] = displayed_count

   

    user_id = update.effective_user.id if update.effective_user else None
    is_group = (
        update.effective_chat is not None
        and update.effective_chat.type in ("group", "supergroup")
    )

    await update.message.reply_text(
        message,
        parse_mode=ParseMode.HTML,
        reply_markup=news_keyboard(user_id if is_group else None),
        disable_web_page_preview=True,
    )
