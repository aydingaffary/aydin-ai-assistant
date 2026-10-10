"""Helpers for keeping each group member's conversation state separate."""

from telegram import Update
from telegram.ext import ContextTypes


def get_member_state(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> dict:
    """Return private user state or per-member state for the current group."""

    chat = update.effective_chat
    user = update.effective_user

    if (
        chat is not None
        and chat.type in ("group", "supergroup")
        and user is not None
    ):
        group_states = context.chat_data.setdefault(
            "group_member_states", {}
        )
        return group_states.setdefault(user.id, {})

    return context.user_data
