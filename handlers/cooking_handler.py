"""Cooking suggestions handler."""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from services.recipe_service import RecipeService
from services.chat_state import get_member_state


def _is_group(update):
    chat = update.effective_chat
    return bool(chat and chat.type in ("group", "supergroup"))


def _state(update, context):
    return get_member_state(update, context)


def _next_callback(update):
    return (
        f"next_recipe_{update.effective_user.id}"
        if _is_group(update)
        else "next_recipe"
    )


async def cooking(update, context):
    """Send the first cooking suggestion."""
    state = _state(update, context)
    service = RecipeService()
    recipe = service.get_recipe()
    state["last_recipe"] = recipe["name"]
    state["recipe_next_count"] = 0
    await send_recipe(update, recipe)


async def next_recipe(update, context):
    """Send another recipe only for the owner of the group button."""
    query = update.callback_query
    state = _state(update, context)

    if _is_group(update):
        parts = query.data.split("_")
        if len(parts) != 3 or not parts[2].isdigit():
            await query.answer("دکمه نامعتبر است.", show_alert=True)
            return
        if int(parts[2]) != update.effective_user.id:
            await query.answer("این پیشنهاد برای عضو دیگری است.", show_alert=True)
            return

    await query.answer()
    count = state.get("recipe_next_count", 0)
    if count >= 3:
        await query.message.reply_text("⛔ سقف پیشنهاد رایگان امروز تمام شد.")
        return

    service = RecipeService()
    last = state.get("last_recipe")
    recipe = service.get_recipe(exclude=last)
    state["last_recipe"] = recipe["name"]
    state["recipe_next_count"] = count + 1

    await query.message.reply_text(
        f"🍲 {recipe['name']}\n\n"
        "مواد لازم:\n" + "\n".join(recipe["ingredients"])
        + "\n\nطرز تهیه:\n" + "\n".join(recipe["steps"])
    )


async def send_recipe(update, recipe):
    text = (
        f"🍲 {recipe['name']}\n\n"
        "مواد لازم:\n" + "\n".join(recipe["ingredients"])
        + "\n\nطرز تهیه:\n" + "\n".join(recipe["steps"])
    )
    keyboard = [[InlineKeyboardButton(
        "🔄 پیشنهاد بعدی", callback_data=_next_callback(update)
    )]]
    await update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )
