"""Admin panel handlers."""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_connection
from services.activity_service import ActivityService
from services.ban_service import BanService
from services.ai_security_service import AISecurityService

security_service = AISecurityService()
ban_service = BanService()

activity_service = ActivityService()


def get_ai_requests(
    status=None,
    limit=20,
):
    """Get AI request logs."""

    with get_connection() as connection:

        if status:

            return connection.execute(
                """
                SELECT
                    user_id,
                    content,
                    status,
                    created_at
                FROM ai_requests
                WHERE status=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (
                    status,
                    limit,
                ),
            ).fetchall()

        return connection.execute(
            """
            SELECT
                user_id,
                content,
                status,
                created_at
            FROM ai_requests
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()


ADMIN_ID = 111228726


def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID


async def check_admin(update: Update) -> bool:

    if not is_admin(update.effective_user.id):

        await update.message.reply_text("❌ دسترسی ندارید.")

        return False

    return True

def get_payments(
    status="pending",
    limit=20,
):
    """Get payment requests."""

    with get_connection() as connection:

        return connection.execute(
            """
            SELECT
                id,
                user_id,
                plan,
                amount,
                status,
                created_at
            FROM payments
            WHERE status=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                status,
                limit,
            ),
        ).fetchall()


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

        users = connection.execute("""
            SELECT user_id, username, is_premium, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 20
            """).fetchall()

    if not users:

        await update.message.reply_text("👥 کاربری وجود ندارد.")

        return

    text = "👥 کاربران اخیر:\n\n"

    for index, user in enumerate(users, 1):

        premium = "⭐ Premium" if user[2] else "رایگان"

        text += (
            f"{index}. "
            f"{user[1] or 'بدون نام'}\n"
            f"ID: {user[0]}\n"
            f"نوع: {premium}\n"
            f"ثبت نام: {user[3][:10]}\n\n"
        )

    await update.message.reply_text(text)


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

    text = "🔥 کاربران فعال امروز:\n\n"

    if not users:

        text += "امروز فعالیتی ثبت نشده."

    else:

        for index, user in enumerate(users, 1):

            text += f"{index}. " f"{user[0] or 'بدون نام'}\n" f"ID: {user[1]}\n\n"

    await update.message.reply_text(text)


async def premium_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    with get_connection() as connection:

        users = connection.execute("""
            SELECT username, user_id
            FROM users
            WHERE is_premium=1
            """).fetchall()

    text = "⭐ کاربران Premium:\n\n"

    if not users:

        text += "هنوز کاربر Premium وجود ندارد."

    else:

        for index, user in enumerate(users, 1):

            text += f"{index}. " f"{user[0] or 'بدون نام'}\n" f"ID: {user[1]}\n\n"

    await update.message.reply_text(text)


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    with get_connection() as connection:

        users = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]

        messages = connection.execute("SELECT COUNT(*) FROM messages").fetchone()[0]

        premium = connection.execute("""
            SELECT COUNT(*)
            FROM users
            WHERE is_premium=1
            """).fetchone()[0]

        activities = connection.execute("""
            SELECT feature, COUNT(*)
            FROM user_activity
            GROUP BY feature
            ORDER BY COUNT(*) DESC
            """).fetchall()

    text = (
        "📊 گزارش کامل ربات\n\n"
        f"👥 کاربران: {users}\n"
        f"💬 پیام‌ها: {messages}\n"
        f"⭐ Premium: {premium}\n\n"
        "🔥 استفاده از بخش‌ها:\n\n"
    )

    for item in activities:

        text += f"• {item[0]} : {item[1]}\n"

    await update.message.reply_text(text)


async def ai_logs(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    requests = get_ai_requests()

    text = "🤖 آخرین درخواست‌های AI:\n\n"

    if not requests:
        text += "درخواستی ثبت نشده."

    else:

        for index, item in enumerate(requests, 1):

            text += (
                f"{index})\n"
                f"👤 ID: {item[0]}\n"
                f"📝 {item[1]}\n"
                f"📌 وضعیت: {item[2]}\n"
                f"🕒 {item[3][:19]}\n\n"
            )

    await update.message.reply_text(text)


async def blocked_requests(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    requests = get_ai_requests(status="blocked")

    text = "🚫 درخواست‌های مسدود شده:\n\n"

    if not requests:
        text += "موردی وجود ندارد."

    else:

        for index, item in enumerate(requests, 1):

            text += (
                f"{index})\n"
                f"👤 ID: {item[0]}\n"
                f"📝 {item[1]}\n"
                f"🕒 {item[3][:19]}\n\n"
            )

    await update.message.reply_text(text)


async def ai_requests(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not await check_admin(update):
        return

    with get_connection() as connection:
        requests = connection.execute("""
            SELECT user_id, content, status, created_at
            FROM ai_requests
            ORDER BY id DESC
            LIMIT 10
            """).fetchall()

    text = "🤖 آخرین درخواست‌های AI:\n\n"

    for i, req in enumerate(requests, 1):
        text += (
            f"{i})\n"
            f"👤 ID: {req[0]}\n"
            f"📝 {req[1]}\n"
            f"📌 {req[2]}\n"
            f"🕒 {req[3][:19]}\n\n"
        )

    await update.message.reply_text(text)


async def ai_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    with get_connection() as connection:

        total = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            """).fetchone()[0]

        allowed = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            WHERE status='allowed'
            """).fetchone()[0]

        blocked = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            WHERE status='blocked'
            """).fetchone()[0]

        users = connection.execute("""
            SELECT COUNT(DISTINCT user_id)
            FROM ai_requests
            """).fetchone()[0]

    text = (
        "🧠 گزارش AI\n\n"
        f"📌 کل درخواست‌ها: {total}\n"
        f"✅ مجاز: {allowed}\n"
        f"🚫 مسدود: {blocked}\n"
        f"👥 کاربران AI: {users}"
    )

    await update.message.reply_text(text)


async def ai_logs(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show recent AI requests."""

    if not await check_admin(update):
        return

    with get_connection() as connection:

        requests = connection.execute("""
            SELECT
                user_id,
                content,
                status,
                created_at
            FROM ai_requests
            ORDER BY id DESC
            LIMIT 10
            """).fetchall()

    if not requests:
        await update.message.reply_text("🤖 هنوز درخواست AI ثبت نشده.")
        return

    text = "🤖 آخرین درخواست‌های AI:\n\n"

    for index, item in enumerate(requests, 1):

        text += (
            f"{index})\n"
            f"👤 ID: {item[0]}\n"
            f"📝 {item[1][:50]}\n"
            f"📌 وضعیت: {item[2]}\n"
            f"🕒 {item[3][:19]}\n\n"
        )

    await update.message.reply_text(text)


async def blocked_requests(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show blocked AI requests."""

    if not await check_admin(update):
        return

    with get_connection() as connection:

        requests = connection.execute("""
            SELECT
                user_id,
                content,
                created_at
            FROM ai_requests
            WHERE status='blocked'
            ORDER BY id DESC
            LIMIT 10
            """).fetchall()

    if not requests:

        await update.message.reply_text("✅ درخواست بلاک شده‌ای وجود ندارد.")

        return

    text = "🚫 درخواست‌های بلاک شده:\n\n"

    for index, item in enumerate(requests, 1):

        text += (
            f"{index})\n"
            f"👤 {item[0]}\n"
            f"📝 {item[1][:50]}\n"
            f"🕒 {item[2][:19]}\n\n"
        )

    await update.message.reply_text(text)


async def ai_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """AI usage statistics."""

    if not await check_admin(update):
        return

    with get_connection() as connection:

        total = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            """).fetchone()[0]

        allowed = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            WHERE status='allowed'
            """).fetchone()[0]

        blocked = connection.execute("""
            SELECT COUNT(*)
            FROM ai_requests
            WHERE status='blocked'
            """).fetchone()[0]

    await update.message.reply_text(
        "📊 آمار AI\n\n"
        f"کل درخواست‌ها: {total}\n"
        f"✅ مجاز: {allowed}\n"
        f"🚫 بلاک شده: {blocked}"
    )


async def ban_user(update, context):

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text("استفاده:\n/ban_user USER_ID")
        return

    user_id = int(context.args[0])

    ban_service.ban_user(user_id, "admin ban")

    await update.message.reply_text(f"🚫 کاربر {user_id} مسدود شد.")


async def unban_user(update, context):

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text("استفاده:\n/unban_user USER_ID")
        return

    user_id = int(context.args[0])

    ban_service.unban_user(user_id)

    await update.message.reply_text(f"✅ کاربر {user_id} آزاد شد.")


async def banned_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    users = ban_service.get_banned_users()

    text = "🚫 کاربران مسدود شده:\n\n"

    if not users:
        text += "لیست خالی است."

    else:
        for i, user in enumerate(users, 1):
            text += f"{i}. ID: {user[0]}\n" f"زمان: {user[1]}\n\n"

    await update.message.reply_text(text)


async def blocked_attempts(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    requests = security_service.get_blocked_attempts()

    if not requests:
        await update.message.reply_text("✅ تلاش مسدود شده‌ای وجود ندارد.")
        return

    text = "🚨 تلاش‌های کاربران مسدود شده:\n\n"

    for index, item in enumerate(requests, 1):

        text += (
            f"{index})\n"
            f"👤 ID: {item[0]}\n"
            f"📝 {item[1]}\n"
            f"🕒 {item[2][:19]}\n\n"
        )

    await update.message.reply_text(text)


async def ai_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    stats = security_service.get_stats()

    text = (
        "📊 آمار هوش مصنوعی\n\n"
        f"👥 کاربران AI: {stats['users']}\n"
        f"💬 کل درخواست‌ها: {stats['total']}\n\n"
        f"✅ مجاز: {stats['allowed']}\n"
        f"🚫 بن شده: {stats['banned']}\n"
        f"⚠️ محدود شده: {stats['rate_limited']}"
    )

    await update.message.reply_text(text)


async def ai_performance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):

    if not await check_admin(update):
        return

    from services.ai_stats_service import AIStatsService

    stats = AIStatsService().get_stats()

    text = "📊 عملکرد هوش مصنوعی\n\n" f"💬 کل درخواست‌ها: {stats['total']}\n\n"

    for provider in stats["providers"]:

        name = provider[0]
        count = provider[1]
        avg_time = provider[2]
        avg_length = provider[3]

        text += (
            f"🤖 {name}\n"
            f"تعداد: {count}\n"
            f"⏱ میانگین زمان: {avg_time:.2f}s\n"
            f"📝 میانگین پاسخ: {avg_length:.0f} کاراکتر\n\n"
        )

        text += "🛡 امنیت:\n\n"

        for item in stats["security"]:

            text += f"• {item[0]} : {item[1]}\n"

    await update.message.reply_text(text)

async def payments_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show pending payments."""

    if not await check_admin(update):
        return

    payments = get_payments()

    if not payments:
        await update.message.reply_text(
            "💳 درخواست پرداختی وجود ندارد."
        )
        return

    text = "💳 درخواست‌های پرداخت:\n\n"

    for payment in payments:

        text += (
            f"🆔 شماره: {payment[0]}\n"
            f"👤 کاربر: {payment[1]}\n"
            f"📦 پلن: {payment[2]}\n"
            f"💰 مبلغ: {payment[3]:,} تومان\n"
            f"⏳ وضعیت: {payment[4]}\n"
            f"📅 تاریخ: {payment[5]}\n\n"
        )

    await update.message.reply_text(text)
