import os
from services.weather_service import WeatherService
from services.ai_service import AIService
from database.db import init_database
from services.limits import UserLimitManager
from dotenv import load_dotenv
from ai_router import AIRouter
from services.limits import UserLimitManager
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
ai_router = AIRouter()
limit_manager = UserLimitManager()
user_service = UserService()
ai_service = AIService()
weather_service = WeatherService()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Return the main menu keyboard."""

    keyboard = [
        ["🧠 دستیار هوشمند", "💵 ارز و طلا"],
        ["📰 اخبار", "⚽ نتایج فوتبال"],
        ["🎬 فیلم و سریال", "⛅ آب‌وهوا"],
        ["🍳 آشپزی", "🧩 چالش روزانه"],
        ["⏰ یادآورها", "✍️ ابزارهای AI"],
        ["📩 ارتباط با سازنده"],
        ["↩️ منوی اصلی"],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""

    context.user_data.pop("mode", None)
    telegram_user = update.effective_user

    user_service.get_or_create_user(
        user_id=telegram_user.id,
        username=telegram_user.username,
    )

    message = (
        "سلام 👋\n\n"
        "به Aydin AI Assistant خوش آمدید.\n\n"
        "من یک دستیار هوش مصنوعی هستم و در آینده می‌توانم "
        "در کارهای مختلفی مثل خلاصه‌سازی، ترجمه، بازنویسی و "
        "پاسخ به سؤال به شما کمک کنم.\n\n"
        "🚀 به‌زودی قابلیت‌های بیشتری اضافه می‌شود."
    )

    reply_markup = get_main_keyboard()

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
    )


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
    user = user_service.get_or_create_user(
        user_id=update.effective_user.id,
        username=update.effective_user.username,
    )
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
        else:
            await update.message.reply_text("✅ قابلیت انتخاب شد.")

        return

    mode = context.user_data.get("mode")

    print("DEBUG MODE:", mode)
    user_id = update.effective_user.id
    if mode == "weather":

        response = weather_service.get_weather(text)

        await update.message.reply_text(response)

        context.user_data.pop("mode", None)
        return

    if mode == "smart_assistant":

        if not limit_manager.can_use_ai(user_id):
            await update.message.reply_text("⛔ سهمیه رایگان امروز شما تمام شده است.")
            return

        response = ai_service.ask(
            user_id=user_id,
            prompt=text,
        )

        limit_manager.record_request(user_id)

        remaining = limit_manager.remaining_requests(user_id)

        await update.message.reply_text(
            response + "\n\n" + f"📊 درخواست رایگان باقی‌مانده امروز: {remaining}"
        )

        context.user_data.pop("mode", None)
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
    init_database()
    """Start the Telegram bot."""

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
    application.add_error_handler(error_handler)
    print("Aydin AI Assistant is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
