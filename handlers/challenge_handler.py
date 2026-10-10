"""Challenge handler."""

from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes
from services.challenge_service import ChallengeService
from services.chat_state import get_member_state

service = ChallengeService()


def _is_group(update):
    chat = update.effective_chat
    return bool(chat and chat.type in ("group", "supergroup"))


def _state(update, context):
    return get_member_state(update, context)


def _owner_callback(update, prefix, value):
    if _is_group(update):
        return f"{prefix}_{update.effective_user.id}_{value}"
    return f"{prefix}_{value}" if value is not None else prefix


def build_keyboard(question, owner_id=None):
    """Create answer buttons; group buttons are bound to their owner."""
    keyboard = []
    for index, option in enumerate(question["options"]):
        callback = (
            f"answer_{owner_id}_{index}"
            if owner_id is not None
            else f"answer_{index}"
        )
        keyboard.append([
            InlineKeyboardButton(option, callback_data=callback)
        ])
    return InlineKeyboardMarkup(keyboard)


async def challenge_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🧩 شروع چالش"],
        ["🏆 رتبه من"],
        ["↩️ منوی اصلی"],
    ]
    await update.message.reply_text(
        "🧩 مسابقه روزانه\n\nیک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def handle_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a challenge for the current user."""
    user_id = update.effective_user.id
    state = _state(update, context)

    if not service.has_username(user_id):
        state["waiting_username"] = True
        await update.message.reply_text(
            "🧩 برای شرکت در مسابقه\n\n"
            "یک نام کاربری دلخواه وارد کنید:\n\n"
            "مثال:\n• Atabak\n• Aynaz\n• Ghazaleh"
        )
        return

    user = service.update_visit(user_id)
    question = service.get_question()
    state["challenge"] = question
    state["challenge_time"] = datetime.now()

    text = (
        "🧩 چالش روزانه\n\n"
        f"📅 مراجعه روزانه: {user['daily_streak']} روز\n"
        f"🔥 پاسخ صحیح پشت سرهم: {user['correct_streak']}\n"
        f"⭐ امتیاز: {user['score']}\n\n"
        f"🎯 {question['question']}\n\n"
        "⏳ فرصت پاسخ: 10 ثانیه"
    )
    owner_id = user_id if _is_group(update) else None
    await update.message.reply_text(
        text,
        reply_markup=build_keyboard(question, owner_id=owner_id),
    )


async def save_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the current user's challenge username."""
    state = _state(update, context)
    if not state.get("waiting_username"):
        return

    username = update.message.text.strip()
    if len(username) < 3:
        await update.message.reply_text("❌ نام باید حداقل ۳ کاراکتر باشد.")
        return

    user_id = update.effective_user.id
    service.save_username(user_id, username)
    state.pop("waiting_username", None)

    await update.message.reply_text(
        f"✅ نام کاربری شما ثبت شد:\n🏆 {username}\n\n"
        "🧩 اولین چالش شما شروع می‌شود!"
    )
    await handle_challenge(update, context)


def _parse_answer_callback(update):
    """Return (owner_id, answer_index) for old and group callback formats."""
    data = update.callback_query.data
    parts = data.split("_")
    if len(parts) == 2:
        return None, int(parts[1])
    if len(parts) == 3:
        return int(parts[1]), int(parts[2])
    raise ValueError("Invalid challenge answer callback")


def _next_callback(update):
    return (
        f"next_challenge_{update.effective_user.id}"
        if _is_group(update)
        else "next_challenge"
    )


async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check an answer, rejecting another group member's buttons."""
    query = update.callback_query
    user_id = update.effective_user.id
    state = _state(update, context)

    try:
        owner_id, selected = _parse_answer_callback(update)
    except (TypeError, ValueError):
        await query.answer("دکمه نامعتبر است.", show_alert=True)
        return

    if _is_group(update) and owner_id != user_id:
        await query.answer("این سؤال برای عضو دیگری است.", show_alert=True)
        return

    await query.answer()
    question = state.get("challenge")
    if not question:
        await query.edit_message_text("❌ چالشی برای شما پیدا نشد.")
        return

    start_time = state.get("challenge_time")
    if start_time and (datetime.now() - start_time).total_seconds() > 10:
        user = service.wrong_answer(user_id)
        state.pop("challenge", None)
        state.pop("challenge_time", None)
        keyboard = [[InlineKeyboardButton(
            "🧩 سوال بعدی", callback_data=_next_callback(update)
        )]]
        await query.edit_message_text(
            "⏰ زمان تمام شد.\n\n"
            "⭐️ -5 امتیاز\n🔥 استریک پاسخ صحیح قطع شد\n"
            f"🏆 امتیاز کل: {user['score']}",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if selected == question["answer"]:
        user = service.correct_answer(user_id)
        text = (
            "✅ درست است!\n\n⭐ +10 امتیاز\n\n"
            f"🔥 استریک پاسخ صحیح: {user['correct_streak']}\n"
            f"📅 مراجعه روزانه: {user['daily_streak']} روز\n"
            f"🏆 امتیاز کل: {user['score']}"
        )
    else:
        user = service.wrong_answer(user_id)
        text = (
            "❌ جواب اشتباه بود.\n\n⭐ -5 امتیاز\n\n"
            "🔥 استریک پاسخ صحیح قطع شد\n"
            f"🏆 امتیاز کل: {user['score']}"
        )

    state.pop("challenge", None)
    state.pop("challenge_time", None)
    keyboard = [[InlineKeyboardButton(
        "🧩 سوال بعدی", callback_data=_next_callback(update)
    )]]
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def next_challenge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the next question to the owner of the callback."""
    query = update.callback_query
    user_id = update.effective_user.id
    state = _state(update, context)
    data = query.data

    if _is_group(update):
        parts = data.split("_")
        if len(parts) != 3 or not parts[2].isdigit():
            await query.answer("دکمه نامعتبر است.", show_alert=True)
            return
        if int(parts[2]) != user_id:
            await query.answer("این دکمه برای عضو دیگری است.", show_alert=True)
            return

    await query.answer()
    question = service.get_question()
    state["challenge"] = question
    state["challenge_time"] = datetime.now()
    owner_id = user_id if _is_group(update) else None

    await query.edit_message_text(
        "🧩 چالش روزانه\n\n"
        f"🎯 {question['question']}\n\n"
        "⏳ فرصت پاسخ: 10 ثانیه",
        reply_markup=build_keyboard(question, owner_id=owner_id),
    )


async def show_rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current user's rank."""
    user_id = update.effective_user.id
    user = service.get_user(user_id)
    rank = service.get_rank(user_id)
    medal = service.get_medal(user["score"])
    total = user.get("total_questions", 0)
    success_rate = int(user.get("correct_answers", 0) / total * 100) if total else 0

    await update.message.reply_text(
        "🏆 وضعیت مسابقه\n\n"
        f"👤 نام: {user.get('username', 'ثبت نشده')}\n\n"
        f"⭐ امتیاز فعلی: {user['score']}\n"
        f"🏅 بهترین رکورد: {user.get('best_score', 0)}\n\n"
        f"🧩 تعداد سوال‌ها: {total}\n"
        f"✅ پاسخ صحیح: {user.get('correct_answers', 0)}\n"
        f"❌ پاسخ غلط: {user.get('wrong_answers', 0)}\n"
        f"📊 درصد موفقیت: {success_rate}%\n\n"
        f"🔥 استریک پاسخ صحیح: {user['correct_streak']} روز\n"
        f"📅 مراجعه روزانه: {user['daily_streak']} روز\n\n"
        f"{medal}\n📊 رتبه شما: {rank}"
    )
