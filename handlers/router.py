"""Telegram bot handlers router."""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    MessageHandler,
    filters,
)


def get_feature_mode(text: str) -> str | None:
    """Return selected feature mode."""

    features = {
        "🧠 دستیار هوشمند": "smart_assistant",
        "💵 ارز و طلا": "currency",
        "⛅ آب‌وهوا": "weather",
    }

    return features.get(text)


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Route user messages."""

    text = update.message.text

    print("ROUTER:", text)

    if text == "↩️ منوی اصلی":
        context.user_data.pop("mode", None)
        return

    mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        if mode == "weather":
            await update.message.reply_text("⛅ لطفاً نام شهر خود را وارد کنید.")
            return

        if mode == "smart_assistant":
            await update.message.reply_text("🧠 لطفاً درخواست خود را ارسال کنید.")
            return

        if mode == "currency":
            from handlers.market_handler import handle_market

            await handle_market(update, context)
            return

    mode = context.user_data.get("mode")
    
    print("CURRENT MODE:", mode)

    if mode == "weather":
        from handlers.weather_handler import handle_weather

        await handle_weather(update, context)
        return

    if mode == "smart_assistant":
        from handlers.ai_handler import handle_ai

        await handle_ai(update, context)
        return


def register_handlers(application):
    """Register telegram handlers."""

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
