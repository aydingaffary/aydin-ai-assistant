
"""Telegram bot handlers router."""

import logging
from datetime import datetime

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, MessageHandler, filters

from handlers.cooking_handler import cooking
from handlers.imdb_handler import handle_movie_search
from handlers.subscription_handler import (
    handle_subscription,
    handle_subscription_plan,
)
from services.activity_service import ActivityService
from services.ai_service import AIService
from services.subscription_service import SubscriptionService
from services.user_service import UserService

logger = logging.getLogger(__name__)

activity_service = ActivityService()
subscription_service = SubscriptionService()


def get_feature_mode(text: str) -> str | None:
    """Return the mode associated with a main-menu button."""

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
        "💎 وضعیت اشتراک": "subscription_status",
    }

    return features.get(text)


async def return_to_main_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Clear all active states and return the user to the main menu."""

    context.user_data.clear()

    from handlers.start_handler import start

    await start(update, context)


async def handle_movie_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show the movie and TV menu."""

    keyboard = [
        ["🔎 جستجوی فیلم"],
        ["🎬 اکران‌های پیش رو"],
        ["📺 سریال‌های پیش رو"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "🎬 فیلم و سریال\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Route incoming text messages to the appropriate handler."""

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    print("ROUTER GOT:", repr(text))
    print("BUTTON:", repr(text))

    logger.info("Router received: %s", text)

 
    # ============================================================
    # GROUP ROUTING — NO AI ASSISTANT
    chat = update.effective_chat

    if chat and chat.type in ("group", "supergroup"):
        from services.chat_state import get_member_state

        state = get_member_state(update, context)

        # Main-menu commands must be handled before pending input states.
        if text in {"↩️ منوی اصلی", "منوی اصلی"}:
            state.clear()
            keyboard = [
                ["💵 ارز و طلا", "📰 اخبار"],
                ["⛅ آب‌وهوا", "⚽ نتایج فوتبال"],
                ["🎬 فیلم و سریال", "🔎 جستجوی فیلم"],
                ["🎬 اکران‌های پیش رو", "📺 سریال‌های پیش رو"],
                ["🍳 آشپزی", "🧩 چالش روزانه"],
                ["👨‍💻 ارتباط با توسعه‌دهنده"],
            ]
            await update.message.reply_text(
                "🏠 منوی اصلی ربات\n\nیک گزینه را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True,
                ),
            )
            return

        market_buttons = {
            "💵 ارز و طلا", "دلار", "قیمت دلار", "قیمت ارز",
            "طلا", "قیمت طلا",
        }
        news_buttons = {
            "📰 اخبار", "اخبار", "خبرها", "آخرین اخبار", "اخبار روز",
        }
        weather_buttons = {
            "⛅ آب‌وهوا", "⛅️ آب‌وهوا", "آب‌وهوا", "آب و هوا",
            "هوا", "وضعیت هوا",
        }
        movie_search_buttons = {"🔎 جستجوی فیلم", "جستجوی فیلم"}
        upcoming_movie_buttons = {"🎬 اکران‌های پیش رو", "اکران‌های پیش رو"}
        upcoming_tv_buttons = {"📺 سریال‌های پیش رو", "سریال‌های پیش رو"}
        cooking_buttons = {"🍳 آشپزی", "آشپزی"}
        football_buttons = {"⚽ نتایج فوتبال", "فوتبال"}
        challenge_buttons = {
            "🧩 چالش روزانه", "چالش روزانه", "چالش", "🧩 چالش",
        }
        developer_buttons = {
            "👨‍💻 ارتباط با توسعه‌دهنده", "ارتباط با توسعه‌دهنده",
        }

        # A new feature selection cancels this member's previous pending input.
        # Keep all feature-button checks above weather/movie follow-up checks.
        if text in market_buttons:
            state.clear()
            from handlers.market_handler import handle_market
            await handle_market(update, context)
            return

        if text in news_buttons:
            state.clear()
            from handlers.news_handler import handle_news
            await handle_news(update, context)
            return

        if text in weather_buttons:
            state.clear()
            state["mode"] = "weather"
            await update.message.reply_text(
                "⛅ نام شهر را وارد کنید؛ مثلاً تبریز یا تهران."
            )
            return

        if text in upcoming_movie_buttons:
            state.clear()
            from handlers.upcoming_handler import handle_upcoming
            await handle_upcoming(update, context)
            return

        if text in upcoming_tv_buttons:
            state.clear()
            from handlers.tv_upcoming_handler import handle_tv_upcoming
            await handle_tv_upcoming(update, context)
            return

        if text in movie_search_buttons:
            state.clear()
            state["waiting_movie"] = True
            await update.message.reply_text(
                "🎬 نام فیلم یا سریال را وارد کنید."
            )
            return

        if text in cooking_buttons:
            state.clear()
            from handlers.cooking_handler import cooking
            await cooking(update, context)
            return

        if text in football_buttons:
            state.clear()
            from handlers.football_handler import handle_football
            await handle_football(update, context)
            return

        if text in challenge_buttons:
            state.clear()
            state["mode"] = "challenge"
            from handlers.challenge_handler import challenge_menu
            await challenge_menu(update, context)
            return

        if text in developer_buttons:
            state.clear()
            await update.message.reply_text(
                "👨‍💻 ارتباط با توسعه‌دهنده:\n"
                "https://t.me/Aydingaffary"
            )
            return

        if state.get("mode") == "challenge":
            if text == "🧩 شروع چالش":
                from handlers.challenge_handler import handle_challenge
                await handle_challenge(update, context)
                return
            if text == "🏆 رتبه من":
                from handlers.challenge_handler import show_rank
                await show_rank(update, context)
                return

        # Pending inputs are checked only after new feature buttons.
        if state.get("mode") == "weather":
            from handlers.weather_handler import handle_weather
            await handle_weather(update, context)
            return

        if state.get("waiting_movie"):
            state.pop("waiting_movie", None)
            from handlers.imdb_handler import handle_movie_search
            await handle_movie_search(update, context)
            return

        # Never use the AI fallback for unrecognized group messages.
        return

    # 1. GLOBAL RETURN TO MAIN MENU
    # ============================================================

    # This MUST be checked before every stateful handler.
    # Otherwise an active state such as weather/news/movie/reminder
    # may consume "↩️ منوی اصلی" as normal user input.
    if text == "↩️ منوی اصلی":
        await return_to_main_menu(update, context)
        return

    # ============================================================
    # 2. STATEFUL HANDLERS
    # ============================================================

    # Reminder conversation
    if context.user_data.get("reminder_step"):
        from handlers.reminder_handler import handle_reminder

        await handle_reminder(update, context)
        return

    # Movie search input
    if context.user_data.get("waiting_movie"):
        context.user_data.pop("waiting_movie", None)

        await handle_movie_search(
            update,
            context,
        )
        return

    # Challenge username registration
    if context.user_data.get("waiting_username"):
        from handlers.challenge_handler import save_username

        await save_username(update, context)
        return

    # ============================================================
    # 3. SUBSCRIPTION PLAN SELECTION
    # ============================================================

    if text in [
        "🟢 اشتراک یک ماهه",
        "🔵 اشتراک سه ماهه",
    ]:
        await handle_subscription_plan(
            update,
            context,
        )
        return

    # ============================================================
    # 4. MAIN MENU BUTTONS
    # ============================================================

    mode = get_feature_mode(text)

    if mode:
        context.user_data["mode"] = mode

        # --------------------------------------------------------
        # Subscription status
        # --------------------------------------------------------

        if mode == "subscription_status":
            user_id = update.effective_user.id

            if subscription_service.has_access(user_id):
                user = UserService().get_user(user_id)

                if user and user.premium_until:
                    premium_until = datetime.fromisoformat(
                        user.premium_until
                    ).strftime("%Y/%m/%d")

                    await update.message.reply_text(
                        "💎 وضعیت اشتراک\n\n"
                        "⭐ اشتراک ویژه فعال است.\n\n"
                        f"📅 تاریخ انقضا: {premium_until}\n\n"
                        "✅ دسترسی شما به ابزارهای اشتراکی فعال است."
                    )
                else:
                    await update.message.reply_text(
                        "💎 وضعیت اشتراک\n\n"
                        "⭐ اشتراک ویژه فعال است.\n\n"
                        "📅 تاریخ انقضا: نامشخص\n\n"
                        "✅ دسترسی شما به ابزارهای اشتراکی فعال است."
                    )
            else:
                await update.message.reply_text(
                    "💎 وضعیت اشتراک\n\n"
                    "🔒 شما اشتراک فعال ندارید.\n\n"
                    "برای استفاده از امکانات ویژه، اشتراک تهیه کنید."
                )

            return

        # --------------------------------------------------------
        # Subscription
        # --------------------------------------------------------

        if mode == "subscription":
            await handle_subscription(
                update,
                context,
            )
            return

        # --------------------------------------------------------
        # Developer
        # --------------------------------------------------------

        if mode == "developer":
            await update.message.reply_text(
                "👨‍💻 ارتباط با توسعه‌دهنده:\n\n"
                "https://t.me/Aydingaffary"
            )
            return

        # --------------------------------------------------------
        # AI tools
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Challenge
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Movie & TV
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Movie search
        # --------------------------------------------------------

        if mode == "imdb_search":
            context.user_data["waiting_movie"] = True

            await update.message.reply_text(
                "🔎 نام فیلم یا سریال را وارد کنید."
            )
            return

        # --------------------------------------------------------
        # Upcoming movies
        # --------------------------------------------------------

        if mode == "upcoming_movies":
            from handlers.upcoming_handler import handle_upcoming

            await handle_upcoming(
                update,
                context,
            )
            return

        # --------------------------------------------------------
        # Upcoming TV
        # --------------------------------------------------------

        if mode == "upcoming_tv":
            from handlers.tv_upcoming_handler import handle_tv_upcoming

            await handle_tv_upcoming(
                update,
                context,
            )
            return

        # --------------------------------------------------------
        # Reminder
        # --------------------------------------------------------

        if mode == "reminder":
            context.user_data["reminder_step"] = "text"

            await update.message.reply_text(
                "⏰ چه چیزی را یادآوری کنم؟"
            )
            return

        # --------------------------------------------------------
        # Weather
        # --------------------------------------------------------

        if mode == "weather":
            await update.message.reply_text(
                "⛅ لطفاً نام شهر را وارد کنید."
            )
            return

        # --------------------------------------------------------
        # News
        # --------------------------------------------------------

        if mode == "news":
            await update.message.reply_text(
                "📰 موضوع خبر را وارد کنید."
            )
            return

        # --------------------------------------------------------
        # Smart Assistant
        # --------------------------------------------------------

        if mode == "smart_assistant":
            await update.message.reply_text(
                "🧠 درخواست خود را ارسال کنید."
            )
            return

        # --------------------------------------------------------
        # Currency / Gold
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Football
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Cooking
        # --------------------------------------------------------

        if mode == "cooking":
            await cooking(
                update,
                context,
            )
            return

    # ============================================================
    # 5. CURRENT MODE
    # ============================================================

    current_mode = context.user_data.get("mode")

    # ------------------------------------------------------------
    # Weather input
    # ------------------------------------------------------------

    if current_mode == "weather":
        from handlers.weather_handler import handle_weather

        await handle_weather(
            update,
            context,
        )
        return

    # ------------------------------------------------------------
    # News input
    # ------------------------------------------------------------

    if current_mode == "news":
        from handlers.news_handler import handle_news

        await handle_news(
            update,
            context,
        )
        return

    # ------------------------------------------------------------
    # Football team search
    # ------------------------------------------------------------

    if current_mode == "football_search":
        from handlers.football_handler import handle_team_search

        await handle_team_search(
            update,
            context,
        )
        return

    # ------------------------------------------------------------
    # Challenge submenu
    # ------------------------------------------------------------

    if current_mode == "challenge":

        if text == "🧩 شروع چالش":
            from handlers.challenge_handler import handle_challenge

            await handle_challenge(
                update,
                context,
            )
            return

        if text == "🏆 رتبه من":
            from handlers.challenge_handler import show_rank

            await show_rank(
                update,
                context,
            )
            return

    # ============================================================
    # 6. SMART ASSISTANT
    # ============================================================

    if current_mode == "smart_assistant":
        user_id = update.effective_user.id

        ai_service = AIService()

        response = ai_service.ask(
            user_id=user_id,
            prompt=text,
        )

        await update.message.reply_text(response)
        return

    # ============================================================
    # 7. FINAL FALLBACK
    # ============================================================

    # Unknown text is still handled by the AI assistant so that
    # free-form AI usage remains available.
    user_id = update.effective_user.id

    ai_service = AIService()

    response = ai_service.ask(
        user_id=user_id,
        prompt=text,
    )

    await update.message.reply_text(response)


def register_handlers(application) -> None:
    """Register router message handlers."""

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message,
        )
    )
