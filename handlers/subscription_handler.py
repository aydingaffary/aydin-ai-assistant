"""Subscription handler."""
from services.payment_service import PaymentService

payment_service = PaymentService()
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes


async def handle_subscription(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show subscription plans."""

    keyboard = [
        ["🟢 اشتراک یک ماهه"],
        ["🔵 اشتراک سه ماهه"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "💎 اشتراک ویژه Aydin AI\n\n"
        "با خرید اشتراک امکانات بیشتری دریافت می‌کنید:\n\n"
        "✅ دسترسی به ابزارهای AI\n"
        "✅ محدودیت کمتر در استفاده\n"
        "✅ قابلیت‌های ویژه آینده\n\n"
        "یکی از پلن‌ها را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )


async def handle_subscription_plan(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle selected subscription plan."""

    text = update.message.text

    if text == "🟢 اشتراک یک ماهه":
        plan = "اشتراک یک ماهه"
        price = "۹۹,۰۰۰ تومان"

    elif text == "🔵 اشتراک سه ماهه":
        plan = "اشتراک سه ماهه"
        price = "۲۵۰,۰۰۰ تومان"

    else:
        return
    payment_service.create_payment(
        user_id=update.effective_user.id,
        plan=plan,
        amount=99000 if "یک" in plan else 250000,
    )
    await update.message.reply_text(
        "💎 درخواست خرید اشتراک\n\n"
        f"📦 پلن انتخابی: {plan}\n"
        f"💰 مبلغ: {price}\n\n"
        "⏳ درگاه پرداخت به‌زودی فعال می‌شود."
    )