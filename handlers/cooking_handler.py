from services.recipe_service import RecipeService
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


async def cooking(update, context):
    """Send first cooking suggestion."""

    service = RecipeService()

    recipe = service.get_recipe()

    context.user_data["last_recipe"] = recipe["name"]
    context.user_data["recipe_next_count"] = 0

    await send_recipe(update, recipe)


async def next_recipe(update, context):

    query = update.callback_query
    await query.answer()

    count = context.user_data.get(
        "recipe_next_count",
        0,
    )

    if count >= 3:
        await query.message.reply_text("⛔ سقف پیشنهاد رایگان امروز تمام شد.")
        return

    service = RecipeService()

    last = context.user_data.get("last_recipe")

    recipe = service.get_recipe(exclude=last)

    context.user_data["last_recipe"] = recipe["name"]
    context.user_data["recipe_next_count"] = count + 1

    await query.message.reply_text(
        f"🍲 {recipe['name']}\n\n"
        "مواد لازم:\n"
        + "\n".join(recipe["ingredients"])
        + "\n\nطرز تهیه:\n"
        + "\n".join(recipe["steps"])
    )


async def send_recipe(update, recipe):

    text = f"🍲 {recipe['name']}\n\n" "مواد لازم:\n" + "\n".join(
        recipe["ingredients"]
    ) + "\n\nطرز تهیه:\n" + "\n".join(recipe["steps"])

    keyboard = [[InlineKeyboardButton("🔄 پیشنهاد بعدی", callback_data="next_recipe")]]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
