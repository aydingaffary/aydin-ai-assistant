"""Telegram bot handlers router."""

from telegram import Update
from telegram.ext import ContextTypes

from handlers.ai_handler import handle_ai
from handlers.market_handler import handle_market
from handlers.weather_handler import handle_weather


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

    if text == "↩️ منوی اصلی":
        context.user_data.pop("mode", None)
        return

    mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        if mode == "weather":
            await update.message.reply_text("⛅ لطفاً نام شهر خود را وارد کنید.")

        elif mode == "smart_assistant":
            await update.message.reply_text("🧠 لطفاً درخواست خود را ارسال کنید.")

        elif mode == "currency":
            await handle_market(update, context)

        return

    mode = context.user_data.get("mode")

    if mode == "weather":
        await handle_weather(update, context)
        return

    if mode == "smart_assistant":
        await handle_ai(update, context)
        return


def register_handlers(application):
    """Register telegram handlers."""

    from telegram.ext import MessageHandler, filters

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
