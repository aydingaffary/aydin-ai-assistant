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

service = ChallengeService()


def build_keyboard(question):
    """Create answer buttons."""

    keyboard = []

    for index, option in enumerate(question["options"]):
        keyboard.append(
            [
                InlineKeyboardButton(
                    option,
                    callback_data=f"answer_{index}",
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


async def challenge_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show challenge menu."""

    keyboard = [
        ["🧩 شروع چالش"],
        ["🏆 رتبه من"],
        ["↩️ منوی اصلی"],
    ]

    await update.message.reply_text(
        "🧩 مسابقه روزانه\n\n" "یک گزینه را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
        ),
    )


async def handle_challenge(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Start challenge."""

    user_id = update.effective_user.id

    if not service.has_username(user_id):

        context.user_data["waiting_username"] = True

        await update.message.reply_text(
            "🧩 برای شرکت در مسابقه\n\n"
            "یک نام کاربری دلخواه وارد کنید:\n\n"
            "مثال:\n"
            "• Atabak\n"
            "• Aynaz\n"
            "• Ghazaleh"
        )

        return

    user = service.update_visit(user_id)

    question = service.get_question()

    context.user_data["challenge"] = question
    context.user_data["challenge_time"] = datetime.now()

    text = (
        "🧩 چالش روزانه\n\n"
        f"📅 مراجعه روزانه: {user['daily_streak']} روز\n"
        f"🔥 پاسخ صحیح پشت سرهم: {user['correct_streak']}\n"
        f"⭐ امتیاز: {user['score']}\n\n"
        f"🎯 {question['question']}\n\n"
        "⏳ فرصت پاسخ: 10 ثانیه"
    )

    await update.message.reply_text(
        text,
        reply_markup=build_keyboard(question),
    )


async def save_username(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Save username."""

    if not context.user_data.get("waiting_username"):
        return

    username = update.message.text.strip()

    if len(username) < 3:

        await update.message.reply_text("❌ نام باید حداقل ۳ کاراکتر باشد.")

        return

    user_id = update.effective_user.id

    service.save_username(
        user_id,
        username,
    )

    context.user_data.pop(
        "waiting_username",
        None,
    )

    await update.message.reply_text(
        f"✅ نام کاربری شما ثبت شد:\n"
        f"🏆 {username}\n\n"
        "🧩 اولین چالش شما شروع می‌شود!"
    )

    await handle_challenge(
        update,
        context,
    )


async def check_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Check selected answer."""

    query = update.callback_query

    await query.answer()

    user_id = update.effective_user.id

    question = context.user_data.get("challenge")

    if not question:

        await query.edit_message_text("❌ چالشی پیدا نشد.")

        return

    start_time = context.user_data.get("challenge_time")

    if start_time:

        elapsed = (datetime.now() - start_time).seconds

        if elapsed > 10:

            user = service.wrong_answer(user_id)

            context.user_data.pop(
                "challenge",
                None,
            )

            context.user_data.pop(
                "challenge_time",
                None,
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🧩 سوال بعدی",
                        callback_data="next_challenge",
                    )
                ]
            ]

            await query.edit_message_text(
                "⏰ زمان تمام شد.\n\n"
                "⭐️ -5 امتیاز\n"
                "🔥 استریک پاسخ صحیح قطع شد\n"
                f"🏆 امتیاز کل: {user['score']}",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

            return

    selected = int(query.data.split("_")[1])

    if selected == question["answer"]:

        user = service.correct_answer(user_id)

        text = (
            "✅ درست است!\n\n"
            "⭐ +10 امتیاز\n\n"
            f"🔥 استریک پاسخ صحیح: "
            f"{user['correct_streak']}\n"
            f"📅 مراجعه روزانه: "
            f"{user['daily_streak']} روز\n"
            f"🏆 امتیاز کل: "
            f"{user['score']}"
        )

    else:

        user = service.wrong_answer(user_id)

        text = (
            "❌ جواب اشتباه بود.\n\n"
            "⭐ -5 امتیاز\n\n"
            "🔥 استریک پاسخ صحیح قطع شد\n"
            f"🏆 امتیاز کل: "
            f"{user['score']}"
        )

    context.user_data.pop(
        "challenge",
        None,
    )

    context.user_data.pop(
        "challenge_time",
        None,
    )

    keyboard = [
        [
            InlineKeyboardButton(
                "🧩 سوال بعدی",
                callback_data="next_challenge",
            )
        ]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def next_challenge(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Send next question."""

    query = update.callback_query

    await query.answer()

    question = service.get_question()

    context.user_data["challenge"] = question

    context.user_data["challenge_time"] = datetime.now()

    await query.edit_message_text(
        "🧩 چالش روزانه\n\n" f"🎯 {question['question']}\n\n" "⏳ فرصت پاسخ: 10 ثانیه",
        reply_markup=build_keyboard(question),
    )


async def show_rank(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show user rank."""

    user_id = update.effective_user.id

    user = service.get_user(user_id)

    rank = service.get_rank(user_id)

    medal = service.get_medal(user["score"])

    total = user.get("total_questions", 0)

    success_rate = 0

    if total:
        success_rate = int(user.get("correct_answers", 0) / total * 100)

    await update.message.reply_text(
        "🏆 وضعیت مسابقه\n\n"
        f"👤 نام: {user.get('username','ثبت نشده')}\n\n"
        f"⭐ امتیاز فعلی: {user['score']}\n"
        f"🏅 بهترین رکورد: {user.get('best_score',0)}\n\n"
        f"🧩 تعداد سوال‌ها: {user.get('total_questions',0)}\n"
        f"✅ پاسخ صحیح: {user.get('correct_answers',0)}\n"
        f"❌ پاسخ غلط: {user.get('wrong_answers',0)}\n"
        f"📊 درصد موفقیت: {success_rate}%\n\n"
        f"🔥 استریک پاسخ صحیح: "
        f"{user['correct_streak']} روز\n"
        f"📅 مراجعه روزانه: "
        f"{user['daily_streak']} روز\n\n"
        f"{medal}\n"
        f"📊 رتبه شما: {rank}"
    )
