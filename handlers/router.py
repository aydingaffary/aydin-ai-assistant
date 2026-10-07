"""Telegram bot handlers router."""

import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)

from handlers.cooking_handler import cooking
from handlers.imdb_handler import handle_movie_search


logger = logging.getLogger(__name__)


def get_feature_mode(text: str) -> str | None:
    """Return selected feature mode."""

    features = {
        "🧠 دستیار هوشمند": "smart_assistant",
        "💵 ارز و طلا": "currency",
        "📰 اخبار": "news",
        "⚽ نتایج فوتبال": "football",
        "⛅ آب‌وهوا": "weather",

        "🎬 فیلم و سریال": "movie",
        "🔎 جستجوی فیلم": "imdb_search",
        "🎬 اکران‌های پیش رو": "upcoming_movies",
        "📺 سریال‌های پیش رو": "upcoming_tv",

        "🍳 آشپزی": "cooking",
    }

    return features.get(text)


async def handle_movie_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show movie submenu."""

    keyboard = [
        ["🔎 جستجوی فیلم"],
        ["🎬 اکران‌های پیش رو"],
        ["📺 سریال‌های پیش رو"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "🎬 فیلم و سریال\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Route user messages."""

    text = update.message.text

    logger.info("Router received message: %s", text)

    if text == "↩️ منوی اصلی":
        context.user_data.clear()
        return

    # دریافت نام فیلم برای جستجو
    if context.user_data.get("waiting_movie"):
        await handle_movie_search(update, context)
        return

    mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        if mode == "movie":
            await handle_movie_menu(update, context)
            return

        if mode == "imdb_search":
            context.user_data["waiting_movie"] = True

            await update.message.reply_text(
                "🔎 نام فیلم یا سریال را وارد کنید."
            )
            return

        if mode == "upcoming_movies":
            from handlers.upcoming_handler import handle_upcoming

            await handle_upcoming(update, context)
            return

        if mode == "upcoming_tv":
            from handlers.tv_upcoming_handler import handle_tv_upcoming

            await handle_tv_upcoming(update, context)
            return

        if mode == "weather":
            await update.message.reply_text(
                "⛅ لطفاً نام شهر خود را وارد کنید."
            )
            return

        if mode == "news":
            await update.message.reply_text(
                "📰 لطفاً موضوع یا کشور مورد نظر خود را وارد کنید."
            )
            return

        if mode == "smart_assistant":
            await update.message.reply_text(
                "🧠 لطفاً درخواست خود را ارسال کنید."
            )
            return

        if mode == "currency":
            from handlers.market_handler import handle_market

            await handle_market(update, context)
            return

        if mode == "football":
            from handlers.football_handler import handle_football

            await handle_football(update, context)
            return

        if mode == "cooking":
            await cooking(update, context)
            return


    mode = context.user_data.get("mode")

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


def register_handlers(application):
    """Register telegram handlers."""

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )