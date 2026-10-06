"""Telegram bot handlers router."""
import logging
from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)
logger = logging.getLogger(__name__)


def get_feature_mode(text: str) -> str | None:
    """Return selected feature mode."""

    features = {
        "🧠 دستیار هوشمند": "smart_assistant",
        "💵 ارز و طلا": "currency",
        "📰 اخبار": "news",
        "⚽ نتایج فوتبال": "football",
        "⛅ آب‌وهوا": "weather",
        "🎬 فیلم و سریال": "imdb",
    }

    return features.get(text)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Route user messages."""

    text = update.message.text

    logger.info("Router received message: %s", text)

    if text == "↩️ منوی اصلی":
        context.user_data.pop("mode", None)
        return

    mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        if mode == "weather":
            await update.message.reply_text(
                "⛅ لطفاً نام شهر خود را وارد کنید."
            )
            return

        if mode == "news":
            await update.message.reply_text(
                "📰 لطفاً موضوع یا کشور مورد نظر خود را وارد کنید.\n\n"
                "مثال:\n"
                "ایران\n"
                "هوش مصنوعی\n"
                "اقتصاد"
            )
            return

        if mode == "smart_assistant":
            await update.message.reply_text(
                "🧠 لطفاً درخواست خود را ارسال کنید."
            )
            return
        if mode == "imdb":
            from handlers.imdb_handler import handle_imdb

            await handle_imdb(update, context)
            return

        if mode == "currency":
            from handlers.market_handler import handle_market

            await handle_market(update, context)
            return

        if mode == "football":
            from handlers.football_handler import handle_football

            await handle_football(update, context)
            return
        if mode == "imdb":
            from handlers.imdb_handler import handle_imdb

            await handle_imdb(update, context)
            return

    mode = context.user_data.get("mode")

    logger.info("Current mode: %s", mode)

    if mode == "weather":
        from handlers.weather_handler import handle_weather

        await handle_weather(update, context)
        return

    if mode == "news":
        from handlers.news_handler import handle_news

        await handle_news(update, context)
        return

    if mode == "smart_assistant":
        from handlers.ai_handler import handle_ai

        await handle_ai(update, context)
        return

    if mode == "football":
        from handlers.football_handler import handle_team_search

        await handle_team_search(update, context)
        return

    if mode == "football_search":
        from handlers.football_handler import handle_team_search

        await handle_team_search(update, context)
        return


def register_handlers(application):
    """Register telegram handlers."""

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )