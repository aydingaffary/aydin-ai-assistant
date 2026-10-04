import os

from services.ai_service import AIService
from database.db import init_database
from services.limits import UserLimitManager
from dotenv import load_dotenv
from handlers.router import register_handlers
from handlers.start_handler import start
from handlers.start_handler import start
from handlers.market_handler import handle_market
from services.market_service import MarketService
from handlers.weather_handler import handle_weather
from handlers.ai_handler import handle_ai
from services.user_service import UserService
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


def get_feature_mode(text: str) -> str | None:
    """Return the internal mode for a menu option."""

    features = {
        "🧠 دستیار هوشمند": "smart_assistant",
        "💵 ارز و طلا": "currency",
        "📰 اخبار": "news",
        "⚽ نتایج فوتبال": "football",
        "🎬 فیلم و سریال": "movies",
        "⛅ آب‌وهوا": "weather",
        "🍳 آشپزی": "cooking",
        "🧩 چالش روزانه": "challenge",
        "⏰ یادآورها": "reminder",
        "✍️ ابزارهای AI": "ai_tools",
        "📩 ارتباط با سازنده": "contact",
    }

    return features.get(text)


def get_feature_response(mode: str) -> str:
    """Return a temporary response for the selected feature."""

    responses = {
        "smart_assistant": "🧠 دستیار هوشمند انتخاب شد.",
        "currency": "💵 بخش ارز و طلا انتخاب شد.",
        "news": "📰 بخش اخبار انتخاب شد.",
        "football": "⚽ بخش نتایج فوتبال انتخاب شد.",
        "movies": "🎬 بخش فیلم و سریال انتخاب شد.",
        "weather": "⛅ بخش آب‌وهوا انتخاب شد.",
        "cooking": "🍳 بخش آشپزی انتخاب شد.",
        "challenge": "🧩 بخش چالش روزانه انتخاب شد.",
        "reminder": "⏰ بخش یادآورها انتخاب شد.",
        "ai_tools": "✍️ ابزارهای AI انتخاب شد.",
        "contact": "📩 بخش ارتباط با سازنده انتخاب شد.",
    }

    return responses.get(
        mode,
        "این قابلیت هنوز پیاده‌سازی نشده است.",
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle menu selections and user input."""

    text = update.message.text

    if text == "↩️ منوی اصلی":
        context.user_data.pop("mode", None)

        await update.message.reply_text(
            "↩️ به منوی اصلی برگشتید.",
            reply_markup=get_main_keyboard(),
        )
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

        else:
            await update.message.reply_text("✅ قابلیت انتخاب شد.")

        return

    mode = context.user_data.get("mode")

    if mode == "weather":
        await handle_weather(update, context)
        return

    if mode == "smart_assistant":
        await handle_ai(update, context)
        return


async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Cancel the current operation."""

    context.user_data.pop("mode", None)

    await update.message.reply_text(
        "❌ عملیات لغو شد.\n\n"
        "برای شروع یک قابلیت، یکی از گزینه‌های منو را انتخاب کنید."
    )


async def error_handler(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle unexpected errors raised by the bot."""

    print(f"Bot error: {context.error}")


def main() -> None:
    """Start the Telegram bot."""

    init_database()

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))

    register_handlers(application)

    application.add_error_handler(error_handler)

    print("Aydin AI Assistant is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
