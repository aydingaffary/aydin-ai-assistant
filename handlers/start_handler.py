"""Start command handler."""

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes

from services.user_service import UserService

user_service = UserService()


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Return the main menu keyboard."""

    keyboard = [
        ["🧠 دستیار هوشمند", "💵 ارز و طلا"],
        ["📰 اخبار", "⚽ نتایج فوتبال"],
        ["🎬 فیلم و سریال", "⛅ آب‌وهوا"],
        ["🍳 آشپزی", "🧩 چالش روزانه"],
        ["⏰ یادآور هوشمند", "✍️ ابزارهای AI"],
        ["💎 خرید اشتراک"],
        ["👨‍💻 ارتباط با توسعه‌دهنده"],
    ]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )


async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle the /start command."""

    context.user_data.pop("mode", None)

    telegram_user = update.effective_user

    user_service.get_or_create_user(
        user_id=telegram_user.id,
        username=telegram_user.username or None,
    )

    message = (
        "سلام 👋\n\n"
        "به Aydin AI Assistant خوش آمدید.\n\n"
        "من یک دستیار هوش مصنوعی هستم و در آینده می‌توانم "
        "در کارهای مختلفی مثل خلاصه‌سازی، ترجمه، بازنویسی و "
        "پاسخ به سؤال به شما کمک کنم.\n\n"
        "🚀 به‌زودی قابلیت‌های بیشتری اضافه می‌شود."
    )

    await update.message.reply_text(
        message,
        reply_markup=get_main_keyboard(),
    )
