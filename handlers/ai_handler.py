"""AI message handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.ai_service import AIService
from services.limits import UserLimitManager

ai_service = AIService()
limit_manager = UserLimitManager()


async def handle_ai(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    print("🔥 AI HANDLER CALLED")
    """Handle AI assistant requests."""

    user_id = update.effective_user.id
    text = update.message.text

    if not limit_manager.can_use_ai(user_id):
        await update.message.reply_text("⛔ سهمیه رایگان امروز شما تمام شده است.")
        return

    response = ai_service.ask(
        user_id=user_id,
        prompt=text,
    )

    limit_manager.record_request(user_id)

    remaining = limit_manager.remaining_requests(user_id)

    await update.message.reply_text(
        response + "\n\n" + f"📊 درخواست رایگان باقی‌مانده امروز: {remaining}"
    )

    context.user_data.pop("mode", None)
