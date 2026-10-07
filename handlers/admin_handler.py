"""Admin panel handlers."""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_connection
from services.activity_service import ActivityService


activity_service = ActivityService()


ADMIN_ID = 111228726


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def check_admin(update: Update) -> bool:

    if not is_admin(update.effective_user.id):

        await update.message.reply_text(
            "❌ دسترسی ندارید."
        )

        return False

    return True


async def admin_panel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Main admin panel."""

    if not await check_admin(update):
        return


    await update.message.reply_text(
        "🤖 پنل مدیریت Aydin AI\n\n"
        "دستورات:\n\n"
        "/users - لیست کاربران\n"
        "/today - کاربران فعال امروز\n"
        "/premium - کاربران اشتراکی\n"
        "/stats - گزارش کامل ربات"
    )


async def users_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return


    with get_connection() as connection:

        users = connection.execute(
            """
            SELECT user_id, username, is_premium, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 20
            """
        ).fetchall()


    if not users:

        await update.message.reply_text(
            "👥 کاربری وجود ندارد."
        )

        return


    text = "👥 کاربران اخیر:\n\n"


    for index, user in enumerate(users, 1):

        premium = (
            "⭐ Premium"
            if user[2]
            else "رایگان"
        )

        text += (
            f"{index}. "
            f"{user[1] or 'بدون نام'}\n"
            f"ID: {user[0]}\n"
            f"نوع: {premium}\n"
            f"ثبت نام: {user[3][:10]}\n\n"
        )


    await update.message.reply_text(
        text
    )



async def today_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return


    today = datetime.now().date().isoformat()


    with get_connection() as connection:

        users = connection.execute(
            """
            SELECT DISTINCT u.username,
                            a.user_id
            FROM user_activity a
            JOIN users u
            ON u.user_id=a.user_id
            WHERE DATE(a.created_at)=?
            """,
            (today,),
        ).fetchall()


    text = (
        "🔥 کاربران فعال امروز:\n\n"
    )


    if not users:

        text += "امروز فعالیتی ثبت نشده."

    else:

        for index, user in enumerate(users,1):

            text += (
                f"{index}. "
                f"{user[0] or 'بدون نام'}\n"
                f"ID: {user[1]}\n\n"
            )


    await update.message.reply_text(
        text
    )



async def premium_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return


    with get_connection() as connection:

        users = connection.execute(
            """
            SELECT username, user_id
            FROM users
            WHERE is_premium=1
            """
        ).fetchall()


    text = (
        "⭐ کاربران Premium:\n\n"
    )


    if not users:

        text += "هنوز کاربر Premium وجود ندارد."

    else:

        for index,user in enumerate(users,1):

            text += (
                f"{index}. "
                f"{user[0] or 'بدون نام'}\n"
                f"ID: {user[1]}\n\n"
            )


    await update.message.reply_text(
        text
    )



async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return


    with get_connection() as connection:

        users = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]


        messages = connection.execute(
            "SELECT COUNT(*) FROM messages"
        ).fetchone()[0]


        premium = connection.execute(
            """
            SELECT COUNT(*)
            FROM users
            WHERE is_premium=1
            """
        ).fetchone()[0]


        activities = connection.execute(
            """
            SELECT feature, COUNT(*)
            FROM user_activity
            GROUP BY feature
            ORDER BY COUNT(*) DESC
            """
        ).fetchall()


    text = (
        "📊 گزارش کامل ربات\n\n"
        f"👥 کاربران: {users}\n"
        f"💬 پیام‌ها: {messages}\n"
        f"⭐ Premium: {premium}\n\n"
        "🔥 استفاده از بخش‌ها:\n\n"
    )


    for item in activities:

        text += (
            f"• {item[0]} : {item[1]}\n"
        )


    await update.message.reply_text(
        text
    )