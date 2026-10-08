"""Subscription handler."""

from telegram import Update, ReplyKeyboardMarkup
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