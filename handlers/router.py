"""Telegram bot handlers router."""

import logging
from handlers.subscription_handler import handle_subscription
from services.activity_service import ActivityService
from handlers.subscription_handler import (
    handle_subscription,
    handle_subscription_plan,
)
from services.subscription_service import SubscriptionService
activity_service = ActivityService()
subscription_service = SubscriptionService()
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
        "⏰ یادآور هوشمند": "reminder",
        "🧩 چالش روزانه": "challenge",
        "👨‍💻 ارتباط با توسعه‌دهنده": "developer",
        "✍️ ابزارهای AI": "ai_tools",
        "💎 خرید اشتراک": "subscription",
    }

    return features.get(text)


async def handle_movie_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    keyboard = [
        ["🔎 جستجوی فیلم"],
        ["🎬 اکران‌های پیش رو"],
        ["📺 سریال‌های پیش رو"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "🎬 فیلم و سریال\n\n" "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    text = update.message.text.strip()

    print("ROUTER GOT:", repr(text))
    print("BUTTON:", repr(text))

    logger.info("Router received: %s", text)

    # ثبت نام چالش
    
        # یادآور
    if context.user_data.get("reminder_step"):

        from handlers.reminder_handler import handle_reminder

        await handle_reminder(update, context)

        return
    
    if text in [
        "🟢 اشتراک یک ماهه",
        "🔵 اشتراک سه ماهه",
    ]:

        await handle_subscription_plan(
            update,
            context,
        )

        return

    
    mode = get_feature_mode(text)

    if mode:

        context.user_data["mode"] = mode

        if mode == "subscription":

            await handle_subscription(
                update,
                context,
            )

            return

        if mode == "developer":

            await update.message.reply_text(
                "👨‍💻 ارتباط با توسعه‌دهنده:\n\n"
                "https://t.me/Aydingaffary"
            )

            return


        if mode == "ai_tools":

            user_id = update.effective_user.id

            if not subscription_service.has_access(user_id):

                await update.message.reply_text(
                    "✍️ ابزارهای AI\n\n"
                    "🔒 برای استفاده از ابزارهای هوش مصنوعی "
                    "نیاز به خرید اشتراک دارید."
                )

                return

            await update.message.reply_text(
                "✍️ ابزارهای AI\n\n"
                "🚀 به‌زودی با مجموعه‌ای از ابزارهای مختلف "
                "هوش مصنوعی در خدمت شما هستیم."
            )

            return


        if mode == "challenge":

            activity_service.log_activity(
                update.effective_user.id,
                "challenge",
            )

            from handlers.challenge_handler import challenge_menu

            await challenge_menu(
                update,
                context,
            )

            return


        if mode == "challenge_rank":

            activity_service.log_activity(
                update.effective_user.id,
                "challenge_rank",
            )

            from handlers.challenge_handler import show_rank

            await show_rank(
                update,
                context,
            )

            return


        if mode == "movie":

            activity_service.log_activity(
                update.effective_user.id,
                "movie",
            )

            await handle_movie_menu(
                update,
                context,
            )

            return


        if mode == "imdb_search":

            context.user_data["waiting_movie"] = True

            await update.message.reply_text(
                "🔎 نام فیلم یا سریال را وارد کنید."
            )

            return


        if mode == "upcoming_movies":

            from handlers.upcoming_handler import handle_upcoming

            await handle_upcoming(
                update,
                context,
            )

            return


        if mode == "upcoming_tv":

            from handlers.tv_upcoming_handler import handle_tv_upcoming

            await handle_tv_upcoming(
                update,
                context,
            )

            return


        if mode == "reminder":

            context.user_data["reminder_step"] = "text"

            await update.message.reply_text(
                "⏰ چه چیزی را یادآوری کنم؟"
            )

            return


        if mode == "weather":

            await update.message.reply_text(
                "⛅ لطفاً نام شهر را وارد کنید."
            )

            return


        if mode == "news":

            await update.message.reply_text(
                "📰 موضوع خبر را وارد کنید."
            )

            return


        if mode == "smart_assistant":

            await update.message.reply_text(
                "🧠 درخواست خود را ارسال کنید."
            )

            return


        if mode == "currency":

            activity_service.log_activity(
                update.effective_user.id,
                "currency",
            )

            from handlers.market_handler import handle_market

            await handle_market(
                update,
                context,
            )

            return


        if mode == "football":

            activity_service.log_activity(
                update.effective_user.id,
                "football",
            )

            from handlers.football_handler import handle_football

            await handle_football(
                update,
                context,
            )

            return


        if mode == "cooking":

            await cooking(
                update,
                context,
            )

            return

def register_handlers(application):

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
