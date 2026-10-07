"""Challenge handler."""

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from services.challenge_service import ChallengeService


service = ChallengeService()


async def handle_challenge(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    question = service.get_question()

    context.user_data["challenge"] = question

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

    await update.message.reply_text(
        f"🧩 چالش روزانه\n\n"
        f"{question['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def check_answer(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    query = update.callback_query
    await query.answer()

    question = context.user_data.get("challenge")

    if not question:
        await query.edit_message_text(
            "❌ چالشی پیدا نشد."
        )
        return


    selected = int(
        query.data.split("_")[1]
    )

    if selected == question["answer"]:
        text = (
            "✅ درست جواب دادی!\n\n"
            "آماده سوال بعدی هستی؟"
        )
    else:
        correct = question["options"][
            question["answer"]
        ]

        text = (
            "❌ جواب اشتباه بود.\n\n"
            f"✅ جواب درست: {correct}"
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
    query = update.callback_query
    await query.answer()

    question = service.get_question()

    context.user_data["challenge"] = question

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

    await query.edit_message_text(
        f"🧩 چالش روزانه\n\n"
        f"{question['question']}",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )