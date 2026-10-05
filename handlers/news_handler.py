"""News handler."""

from telegram import Update
from telegram.ext import ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.ai_usage_service import AIUsageService
from services.news_service import NewsService
from services.subscription_service import SubscriptionService


usage_service = AIUsageService()
news_service = NewsService()
subscription_service = SubscriptionService()


async def handle_news(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle news requests."""

    user_id = update.effective_user.id
    topic = update.message.text
    context.user_data["last_news_topic"] = topic

    is_premium = subscription_service.has_access(user_id)

    # کاربران رایگان: روزانه یک بار
    if not is_premium:
        if not usage_service.can_use_ai(
            user_id,
            "news",
        ):
            await update.message.reply_text(
                "🔒 سهمیه رایگان اخبار امروز شما تمام شده است.\n\n"
                "برای دسترسی بیشتر، اشتراک تهیه کنید."
            )
            return

    news = news_service.get_news(
        topic,
        limit=3 if not is_premium else 10,
    )

    if not news:
        await update.message.reply_text(
            f"❌ خبری درباره «{topic}» پیدا نشد."
        )
        return

    response = f"📰 اخبار درباره {topic}\n\n"

    for index, item in enumerate(news, start=1):
        response += (
            f"{index}. {item['title']}\n"
            f"🌐 {item['source']}\n"
            f"🔗 {item['link']}\n\n"
        )

    if not is_premium:
        usage_service.consume_ai(
            user_id,
            "news",
        )

        response += (
            "🔒 برای مشاهده اخبار بیشتر و دسترسی نامحدود "
            "اشتراک تهیه کنید."
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "📰 اخبار بیشتر",
                callback_data="news_more",
            )
        ]   
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        response,
        reply_markup=reply_markup,
    )