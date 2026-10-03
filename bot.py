import os

from dotenv import load_dotenv
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

    

    return features.get(text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""

    context.user_data.pop("mode", None)

 

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
    if text == "↩️ منوی اصلی":
        context.user_data.pop("mode", None)

        await update.message.reply_text(
            "↩️ به منوی اصلی برگشتید.",
            reply_markup=get_main_keyboard(),
        )
        return

        features = {
        "🧠 دستیار هوشمند": (
            "smart_assistant",
            "سؤال یا درخواست خود را بنویسید.",
        ),
        "💵 ارز و طلا": (
            "currency",
            "نوع ارز یا قیمت موردنظر خود را بنویسید.",
        ),
        "📰 اخبار": (
            "news",
            "موضوع خبری موردنظر خود را بنویسید.",
        ),
        "⚽ نتایج فوتبال": (
            "football",
            "نام لیگ یا تیم موردنظر را بنویسید.",
        ),
        "🎬 فیلم و سریال": (
            "movies",
            "نام فیلم، سریال یا موضوع موردنظر را بنویسید.",
        ),
        "⛅ آب‌وهوا": (
            "weather",
            "نام شهر موردنظر را بنویسید.",
        ),
        "🍳 آشپزی": (
            "cooking",
            "نام غذا یا مواد اولیه را بنویسید.",
        ),
        "🧩 چالش روزانه": (
            "challenge",
            "برای دریافت چالش روزانه آماده‌اید؟",
        ),
        "⏰ یادآورها": (
            "reminder",
            "یادآوری موردنظر خود را بنویسید.",
        ),
        "✍️ ابزارهای AI": (
            "ai_tools",
            "نوع ابزار موردنظر را انتخاب یا درخواست خود را بنویسید.",
        ),
        "📩 ارتباط با سازنده": (
            "contact",
            "پیام خود را برای سازنده ربات بنویسید.",
        ),
    }

        mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        await update.message.reply_text(
            "✅ قابلیت انتخاب شد.\n\n"
            "لطفاً درخواست خود را ارسال کنید."
        )
        return

        mode = context.user_data.get("mode")

    if mode:
        response = get_feature_response(mode)

        await update.message.reply_text(
            response
            + "\n\n"
            + "📌 درخواست شما دریافت شد.\n"
            + "موتور اصلی این قابلیت هنوز متصل نشده است."
        )

        context.user_data.pop("mode", None)
        return

    await update.message.reply_text(
        "لطفاً ابتدا یکی از گزینه‌های منو را انتخاب کنید."
    )

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


def main() -> None:
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

    print("Aydin AI Assistant is running...")

    application.run_polling()


if __name__ == "__main__":
    main()
