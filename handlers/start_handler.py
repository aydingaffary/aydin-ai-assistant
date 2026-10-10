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
        ["💎 وضعیت اشتراک"],
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

    message = message = (
    "سلام 👋 به Aydin AI Assistant خوش آمدید!\n\n"
    "من دستیار هوشمند شما برای دسترسی سریع‌تر به اطلاعات "
    "و ابزارهای کاربردی هستم. 🤖\n\n"
    "از منوی زیر می‌توانید به قابلیت‌های مختلف ربات دسترسی داشته باشید:\n\n"
    "🧠 دستیار هوشمند\n"
    "📰 اخبار\n"
    "⚽ نتایج فوتبال\n"
    "💵 ارز و طلا\n"
    "⛅ آب‌وهوا\n"
    "🎬 فیلم و سریال\n"
    "🍳 آشپزی\n"
    "⏰ یادآور هوشمند\n\n"
    "🚀 به‌زودی با مجموعه‌ای از ابزارهای متنوع هوش مصنوعی "
    "نیز در خدمت شما خواهیم بود.\n\n"
    "برای شروع، یکی از گزینه‌های منو را انتخاب کنید. 🌟"
)

    await update.message.reply_text(
        message,
        reply_markup=get_main_keyboard(),
    )
