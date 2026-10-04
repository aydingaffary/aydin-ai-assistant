"""Market message handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.market_service import MarketService

market_service = MarketService()


async def handle_market(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle currency and gold market request."""

    response = market_service.get_market_report()

    await update.message.reply_text(response)

    context.user_data.pop("mode", None)
