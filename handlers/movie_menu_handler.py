"""Movie menu handler."""

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes


async def handle_movie_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show movie options."""

    keyboard = [
        ["🔎 جستجوی فیلم"],
        ["🎬 اکران‌های پیش رو"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "🎬 بخش فیلم و سریال\n\n" "لطفاً یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )
