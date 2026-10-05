"""News more handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.news_service import NewsService
from services.subscription_service import SubscriptionService


news_service = NewsService()
subscription_service = SubscriptionService()


async def handle_news_more(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle more news requests."""

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id

    if not subscription_service.has_access(user_id):
        await query.edit_message_text(
            "🔒 برای مشاهده اخبار بیشتر نیاز به اشتراک دارید."
        )
        return

    topic = context.user_data.get(
        "last_news_topic",
        "",
    )

    news = news_service.get_news(
        topic,
        limit=10,
    )

    response = "📰 اخبار بیشتر:\n\n"

    for index, item in enumerate(news, start=1):
        response += (
            f"{index}. {item['title']}\n"
            f"🌐 {item['source']}\n"
            f"🔗 {item['link']}\n\n"
        )

    await query.edit_message_text(response)