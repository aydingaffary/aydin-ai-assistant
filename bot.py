import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler

from database.db import init_database
from handlers.router import register_handlers
from handlers.start_handler import start

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")


async def cancel(update, context):
    """Cancel the current operation."""

    context.user_data.pop("mode", None)

    await update.message.reply_text(
        "❌ عملیات لغو شد.\n\n"
        "برای شروع یک قابلیت، یکی از گزینه‌های منو را انتخاب کنید."
    )


async def error_handler(update, context):
    """Handle unexpected errors."""

    print(f"Bot error: {context.error}")


def main():
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
