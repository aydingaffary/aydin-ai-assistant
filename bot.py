import os
from telegram import Update, ReplyKeyboardMarkup
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""

    message = (
    "سلام 👋\n\n"
    "به Aydin AI Assistant خوش آمدید.\n\n"
    "من یک دستیار هوش مصنوعی هستم و در آینده می‌توانم "
    "در کارهای مختلفی مثل خلاصه‌سازی، ترجمه، بازنویسی و "
    "پاسخ به سؤال به شما کمک کنم.\n\n"
    "🚀 به‌زودی قابلیت‌های بیشتری اضافه می‌شود."
)

    keyboard = [
        ["📝 خلاصه‌سازی", "🌍 ترجمه"],
        ["✍️ بازنویسی", "💡 ایده‌پردازی"],
        ["❓ پرسش از AI", "📧 نوشتن ایمیل"],
        ["📱 ساخت کپشن", "🛍️ توضیحات محصول"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
    )

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle menu button selections."""

    text = update.message.text

    if text == "📝 خلاصه‌سازی":
        response = "📝 قابلیت خلاصه‌سازی انتخاب شد.\n\nلطفاً متنی را که می‌خواهید خلاصه شود ارسال کنید."

    elif text == "🌍 ترجمه":
        response = "🌍 قابلیت ترجمه انتخاب شد.\n\nلطفاً متنی را که می‌خواهید ترجمه شود ارسال کنید."

    elif text == "✍️ بازنویسی":
        response = "✍️ قابلیت بازنویسی انتخاب شد.\n\nلطفاً متن موردنظر را ارسال کنید."

    elif text == "💡 ایده‌پردازی":
        response = "💡 قابلیت ایده‌پردازی انتخاب شد.\n\nموضوعی که برای آن ایده می‌خواهید را بنویسید."

    elif text == "❓ پرسش از AI":
        response = "❓ سؤال خود را برای AI بنویسید."

    elif text == "📧 نوشتن ایمیل":
        response = "📧 موضوع و توضیح کوتاهی درباره ایمیلی که می‌خواهید بنویسید ارسال کنید."

    elif text == "📱 ساخت کپشن":
        response = "📱 موضوع یا عکس موردنظر برای ساخت کپشن را ارسال کنید."

    elif text == "🛍️ توضیحات محصول":
        response = "🛍️ نام محصول و اطلاعات آن را ارسال کنید."

    else:
        return

    await update.message.reply_text(response)
def main() -> None:
    """Start the Telegram bot."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)
)
    print("Aydin AI Assistant is running...")

    application.run_polling()


if __name__ == "__main__":
    main()