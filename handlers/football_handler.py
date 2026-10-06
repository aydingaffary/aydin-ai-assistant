"""Football handler."""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from services.football_service import FootballService
from services.team_service import TeamService

team_service = TeamService()


async def handle_football(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show football menu."""

    keyboard = [
        [
            InlineKeyboardButton(
                "🔴 نتایج زنده",
                callback_data="live_scores",
            )
        ],
        [
            InlineKeyboardButton(
                "➕ افزودن تیم",
                callback_data="add_team_menu",
            )
        ],
        [
            InlineKeyboardButton(
                "⭐ تیم‌های من",
                callback_data="my_teams",
            )
        ],
        [
            InlineKeyboardButton(
                "🗑 حذف تیم",
                callback_data="remove_team_menu",
            )
        ],
        [
            InlineKeyboardButton(
                "↩️ منوی اصلی",
                callback_data="main_menu",
            )
        ],
    ]

    await update.message.reply_text(
        "⚽ بخش فوتبال\n\n"
        "با انتخاب تیم‌های مورد علاقه:\n"
        "✅ نتیجه زنده بازی‌ها را ببینید\n"
        "✅ هنگام گل و تغییر نتیجه اعلان دریافت کنید\n\n"
        "یک گزینه را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def handle_team_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Search football team."""

    text = update.message.text

    teams = FootballService().search_team(text)

    if not teams:
        await update.message.reply_text(
            "❌ تیمی پیدا نشد.\n" "نام دیگری را امتحان کنید."
        )
        return

    keyboard = []

    for team in teams:
        keyboard.append(
            [
                InlineKeyboardButton(
                    team["name"],
                    callback_data=f"add_team_{team['id']}",
                )
            ]
        )

    await update.message.reply_text(
        "⚽ تیم‌های پیدا شده:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def add_team_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Add selected team."""

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    team_id = int(
        query.data.replace(
            "add_team_",
            "",
        )
    )

    team = FootballService().get_team(team_id)

    if not team:
        await query.edit_message_text("❌ تیم پیدا نشد.")
        return

    team_service.add_team(
        user_id,
        team["id"],
        team["name"],
    )

    await query.edit_message_text(f"✅ {team['name']} اضافه شد.")


async def show_my_teams(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show user's favorite teams."""

    query = update.callback_query
    await query.answer()

    teams = team_service.get_teams(query.from_user.id)

    if not teams:
        text = "❌ هنوز تیمی انتخاب نکرده‌اید."
    else:
        text = "⭐ تیم‌های شما:\n\n"

        for team in teams:
            text += f"⚽ {team['team_name']}\n"

    await query.edit_message_text(text)


async def start_team_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Start team search."""

    query = update.callback_query
    await query.answer()

    context.user_data["mode"] = "football_search"

    await query.edit_message_text(
        "⚽ نام تیم مورد نظر را وارد کنید.\n\n"
        "مثال:\n"
        "رئال مادرید\n"
        "Juventus\n"
        "تراکتور"
    )


async def show_live_scores(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show current live football matches."""

    query = update.callback_query
    await query.answer()

    matches = FootballService().get_live_matches()

    if not matches:
        await query.edit_message_text("🔴 در حال حاضر بازی زنده‌ای پیدا نشد.")
        return

    text = "🔴 بازی‌های زنده:\n\n"

    for match in matches:
        home = match.get(
            "home_team",
            "Unknown",
        )
        away = match.get(
            "away_team",
            "Unknown",
        )

        home_score = match.get("home_score")
        away_score = match.get("away_score")

        text += f"⚽ {home} " f"{home_score} - " f"{away_score} " f"{away}\n\n"

    await query.edit_message_text(text)


async def start_remove_team(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Show teams available for removal."""

    query = update.callback_query
    await query.answer()

    teams = team_service.get_teams(query.from_user.id)

    if not teams:
        await query.edit_message_text("❌ تیمی برای حذف وجود ندارد.")
        return

    keyboard = []

    for team in teams:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"🗑 {team['team_name']}",
                    callback_data=(f"remove_team_{team['team_id']}"),
                )
            ]
        )

    await query.edit_message_text(
        "🗑 تیم مورد نظر برای حذف را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def remove_team_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Remove selected favorite team."""

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    team_id = int(
        query.data.replace(
            "remove_team_",
            "",
        )
    )

    team_service.remove_team(
        user_id,
        team_id,
    )

    await query.edit_message_text("✅ تیم با موفقیت حذف شد.")
