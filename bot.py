
import logging
from handlers.challenge_handler import (
    check_answer,
    next_challenge,
)
from handlers.admin_handler import admin_panel
from logging_config import setup_logging
from services.reminder_job import check_reminders
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from handlers.admin_handler import (
    admin_panel,
    users_list,
    today_users,
    premium_users,
    stats,
)
from handlers.challenge_handler import check_answer
from handlers.cooking_handler import (
    cooking,
    next_recipe,
)
from handlers.news_more_handler import handle_news_more
from database.db import init_database
from handlers.router import register_handlers
from handlers.start_handler import start
from handlers.football_handler import (
    add_team_callback,
    remove_team_callback,
    show_live_scores,
    show_my_teams,
    start_remove_team,
    start_team_search,
)
from services.football_monitor import FootballMonitor
from services.football_notification_pipeline import (
    FootballNotificationPipeline,
)
from services.football_notification_router import (
    FootballNotificationRouter,
)
from services.football_provider_manager import (
    FootballProviderManager,
)
from services.football_scheduler import (
    FootballScheduler,
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
async def post_init(application):
    """Start background services."""

    football_scheduler = FootballScheduler(
        pipeline=FootballNotificationPipeline(
            monitor=FootballMonitor(
                provider_manager=FootballProviderManager()
            )
        ),
        router=FootballNotificationRouter(),
    )

    application.bot_data["football_scheduler"] = (
        football_scheduler
    )

    await football_scheduler.start(
        application
    )


async def post_shutdown(application):
    """Stop background services."""

    football_scheduler = (
        application.bot_data.get(
            "football_scheduler"
        )
    )

    if football_scheduler is not None:
        await football_scheduler.stop()

def main():
    """Start the Telegram bot."""
    setup_logging()
    init_database()

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set.")

    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
        
    )
    if application.job_queue:
        application.job_queue.run_repeating(
            check_reminders,
            interval=30,
            first=10,
        )


    # Commands
    application.add_handler(
        CommandHandler(
            "start",
            start,
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            next_challenge,
            pattern="^next_challenge$",
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            check_answer,
            pattern="^answer_",
        )
    )


    application.add_handler(
        CallbackQueryHandler(
            next_recipe,
            pattern="^next_recipe$",
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
    # Football: live scores
    application.add_handler(
        CallbackQueryHandler(
            show_live_scores,
            pattern="^live_scores$",
        )
    )

    # Football: remove team menu
    application.add_handler(
        CallbackQueryHandler(
            start_remove_team,
            pattern="^remove_team_menu$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            check_answer,
            pattern="^answer_",
        )
    )


    # Football: remove selected team
    application.add_handler(
        CallbackQueryHandler(
            remove_team_callback,
            pattern="^remove_team_",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            next_recipe,
            pattern="^next_recipe$"
        )
    )   
    application.add_handler(
        CommandHandler(
            "admin",
            admin_panel,
        )
    )
    application.add_handler(
    CommandHandler(
        "admin",
        admin_panel,
    )
)

    application.add_handler(
        CommandHandler(
            "users",
            users_list,
        )
    )

    application.add_handler(
        CommandHandler(
            "today",
            today_users,
        )
    )

    application.add_handler(
        CommandHandler(
            "premium",
            premium_users,
        )
    )

    application.add_handler(
        CommandHandler(
            "stats",
            stats,
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
    main()