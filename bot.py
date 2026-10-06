
import logging

from logging_config import setup_logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)

from handlers.news_more_handler import handle_news_more
from database.db import init_database
from handlers.router import register_handlers
from handlers.start_handler import start
from handlers.football_handler import (
    add_team_callback,
    show_my_teams,
    start_team_search,
)

from config import BOT_TOKEN


async def cancel(update, context):
    """Cancel the current operation."""

    context.user_data.pop("mode", None)

    await update.message.reply_text(
        "❌ عملیات لغو شد.\n\n"
        "برای شروع یک قابلیت، یکی از گزینه‌های منو را انتخاب کنید."
    )


async def error_handler(update, context):
    """Handle unexpected errors."""

    logging.getLogger(__name__).exception(
        "Bot error",
        exc_info=context.error,
    )

def main():
    """Start the Telegram bot."""
    setup_logging()
    init_database()

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # Commands
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CommandHandler(
            "cancel",
            cancel,
        )
    )

    # News more
    application.add_handler(
        CallbackQueryHandler(
            handle_news_more,
            pattern="^news_more$",
        )
    )

    # Football: show user's teams
    application.add_handler(
        CallbackQueryHandler(
            show_my_teams,
            pattern="^my_teams$",
        )
    )

    # Football: start adding team
    application.add_handler(
        CallbackQueryHandler(
            start_team_search,
            pattern="^add_team_menu$",
        )
    )

    # Football: save selected team
    application.add_handler(
        CallbackQueryHandler(
            add_team_callback,
            pattern="^add_team_",
        )
    )

    # Text router
    register_handlers(application)

    application.add_error_handler(
        error_handler
    )

    logging.getLogger(__name__).info(
        "Aydin AI Assistant is running..."
    )

    application.run_polling()


if __name__ == "__main__":
    main()