
"""Admin panel handlers."""

from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from database.db import get_connection
from services.ai_security_service import AISecurityService
from services.activity_service import ActivityService
from services.ban_service import BanService
from services.payment_service import PaymentService
from database.db import get_connection

ADMIN_ID = 111228726

payment_service = PaymentService()
security_service = AISecurityService()
ban_service = BanService()
activity_service = ActivityService()


def is_admin(user_id: int) -> bool:
    """Return True if the user is an admin."""
    return user_id == ADMIN_ID


async def check_admin(update: Update) -> bool:
    """Check admin access."""
    if not update.effective_user or not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ دسترسی ندارید.")
        return False

    return True


def get_ai_requests(
    status: str | None = None,
    limit: int = 20,
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
                WHERE status = ?
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


def get_payments(
    status: str = "pending",
    limit: int = 20,
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
            WHERE status = ?
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
    """Show the main admin panel."""

    if not await check_admin(update):
        return

    await update.message.reply_text(
        "🤖 پنل مدیریت Aydin AI\n\n"
        "👥 کاربران\n"
        "/users - کاربران اخیر\n"
        "/today - کاربران فعال امروز\n"
        "/premium - کاربران Premium\n\n"
        "📊 آمار\n"
        "/stats - گزارش کامل ربات\n"
        "/ai_stats - آمار هوش مصنوعی\n"
        "/ai_performance - عملکرد AI\n\n"
        "🤖 مانیتورینگ AI\n"
        "/ai_logs - آخرین درخواست‌های AI\n"
        "/blocked - درخواست‌های مسدود شده\n"
        "/blocked_attempts - تلاش‌های مسدود شده\n\n"
        "🚫 مدیریت کاربران\n"
        "/banned - کاربران مسدود شده\n"
        "/ban_user USER_ID - مسدود کردن کاربر\n"
        "/unban_user USER_ID - رفع مسدودی\n\n"
        "💳 پرداخت\n"
        "/payments - پرداخت‌های در انتظار\n"
        "/approve PAYMENT_ID - تأیید پرداخت"
    )


async def users_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show recent users."""

    if not await check_admin(update):
        return

    with get_connection() as connection:
        users = connection.execute(
            """
            SELECT
                user_id,
                username,
                is_premium,
                created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 20
            """
        ).fetchall()

    if not users:
        await update.message.reply_text("👥 کاربری وجود ندارد.")
        return

    text = "👥 کاربران اخیر:\n\n"

    for index, user in enumerate(users, 1):

        premium = "⭐ Premium" if user[2] else "رایگان"

        text += (
            f"{index}. {user[1] or 'بدون نام'}\n"
            f"ID: {user[0]}\n"
            f"نوع: {premium}\n"
            f"ثبت نام: {user[3][:10]}\n\n"
        )

    await update.message.reply_text(text)


async def today_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show users active today."""

    if not await check_admin(update):
        return

    today = datetime.now().date().isoformat()

    with get_connection() as connection:
        users = connection.execute(
            """
            SELECT DISTINCT
                u.username,
                a.user_id
            FROM user_activity a
            JOIN users u
                ON u.user_id = a.user_id
            WHERE DATE(a.created_at) = ?
            ORDER BY a.user_id
            """,
            (today,),
        ).fetchall()

    text = "🔥 کاربران فعال امروز:\n\n"

    if not users:
        text += "امروز فعالیتی ثبت نشده."

    else:
        for index, user in enumerate(users, 1):
            text += (
                f"{index}. {user[0] or 'بدون نام'}\n"
                f"ID: {user[1]}\n\n"
            )

    await update.message.reply_text(text)
async def ai_requests(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if not await check_admin(update):
        return

    with get_connection() as connection:
        requests = connection.execute(
            """
            SELECT user_id, content, status, created_at
            FROM ai_requests
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()

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


async def premium_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show premium users."""

    if not await check_admin(update):
        return

    with get_connection() as connection:
        users = connection.execute(
            """
            SELECT
                username,
                user_id,
                premium_until
            FROM users
            WHERE is_premium = 1
            ORDER BY premium_until DESC
            """
        ).fetchall()

    text = "⭐ کاربران Premium:\n\n"

    if not users:
        text += "هنوز کاربر Premium وجود ندارد."

    else:
        for index, user in enumerate(users, 1):

            expiry = user[2][:10] if user[2] else "نامشخص"

            text += (
                f"{index}. {user[0] or 'بدون نام'}\n"
                f"ID: {user[1]}\n"
                f"انقضا: {expiry}\n\n"
            )

    await update.message.reply_text(text)


async def user_info(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show detailed information about a user."""

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ شناسه کاربر را وارد کنید.\n\n"
            "مثال:\n"
            "/user 111228726"
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ شناسه کاربر باید عدد باشد."
        )
        return

    if user_id <= 0:
        await update.message.reply_text(
            "❌ USER_ID نامعتبر است."
        )
        return

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT
                user_id,
                username,
                is_premium,
                premium_until,
                created_at
            FROM users
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()

    if not user:
        await update.message.reply_text(
            "❌ کاربر پیدا نشد."
        )
        return

    banned = ban_service.is_banned(user_id)

    premium = "⭐ فعال" if user[2] else "🔒 غیرفعال"

    if user[3]:
        premium_until = user[3][:10]
    else:
        premium_until = "نامشخص"

    ban_status = "🚫 مسدود" if banned else "✅ آزاد"

    text = (
        "👤 اطلاعات کاربر\n\n"
        f"ID: {user[0]}\n"
        f"Username: @{user[1] if user[1] else 'بدون نام'}\n\n"
        f"⭐ Premium: {premium}\n"
        f"📅 انقضا: {premium_until}\n"
        f"🚫 وضعیت: {ban_status}\n"
        f"📅 عضویت: {user[4][:10]}"
    )

    await update.message.reply_text(text)


async def stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show general bot statistics."""

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
            WHERE is_premium = 1
            """
        ).fetchone()[0]

        activities = connection.execute(
            """
            SELECT
                feature,
                COUNT(*)
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

    if activities:
        for item in activities:
            text += f"• {item[0]} : {item[1]}\n"
    else:
        text += "هنوز فعالیتی ثبت نشده."

    await update.message.reply_text(text)


async def ai_logs(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show recent AI requests."""

    if not await check_admin(update):
        return

    requests = get_ai_requests(limit=10)

    if not requests:
        await update.message.reply_text(
            "🤖 هنوز درخواست AI ثبت نشده."
        )
        return

    text = "🤖 آخرین درخواست‌های AI:\n\n"

    for index, item in enumerate(requests, 1):

        content = item[1][:50]

        text += (
            f"{index})\n"
            f"👤 ID: {item[0]}\n"
            f"📝 {content}\n"
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

    requests = get_ai_requests(
        status="banned",
        limit=10,
    )

    if not requests:
        await update.message.reply_text(
            "✅ درخواست بلاک شده‌ای وجود ندارد."
        )
        return

    text = "🚫 درخواست‌های بلاک شده:\n\n"

    for index, item in enumerate(requests, 1):

        text += (
            f"{index})\n"
            f"👤 ID: {item[0]}\n"
            f"📝 {item[1][:50]}\n"
            f"🕒 {item[3][:19]}\n\n"
        )

    await update.message.reply_text(text)

async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_admin(update):
        return

    with get_connection() as connection:
        users = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()[0]

        premium = connection.execute(
            "SELECT COUNT(*) FROM users WHERE is_premium = 1"
        ).fetchone()[0]

        total_requests = connection.execute(
            "SELECT COUNT(*) FROM ai_requests"
        ).fetchone()[0]

        allowed = connection.execute(
            "SELECT COUNT(*) FROM ai_requests WHERE status = ?",
            ("allowed",),
        ).fetchone()[0]

        blocked = connection.execute(
            "SELECT COUNT(*) FROM ai_requests WHERE status = ?",
            ("blocked",),
        ).fetchone()[0]

        rate_limited = connection.execute(
            "SELECT COUNT(*) FROM ai_requests WHERE status = ?",
            ("rate_limited",),
        ).fetchone()[0]

        providers = connection.execute(
            """
            SELECT provider, COUNT(*)
            FROM ai_requests
            GROUP BY provider
            ORDER BY COUNT(*) DESC
            """
        ).fetchall()

    text = (
        "📊 مانیتورینگ سیستم\n\n"
        "👥 کاربران\n"
        f"├─ کل کاربران: {users}\n"
        f"└─ Premium فعال: {premium}\n\n"
        "🤖 هوش مصنوعی\n"
        f"├─ کل درخواست‌ها: {total_requests}\n"
        f"├─ موفق: {allowed}\n"
        f"├─ مسدود: {blocked}\n"
        f"└─ Rate Limit: {rate_limited}\n\n"
        "🔌 Providerها\n"
    )

    if providers:
        for provider, count in providers:
            text += f"├─ {provider}: {count} درخواست\n"
    else:
        text += "└─ هنوز داده‌ای ثبت نشده است.\n"

    await update.message.reply_text(text)



async def ai_stats(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show AI security statistics."""

    if not await check_admin(update):
        return

    stats_data = security_service.get_stats()

    text = (
        "📊 آمار هوش مصنوعی\n\n"
        f"👥 کاربران AI: {stats_data['users']}\n"
        f"💬 کل درخواست‌ها: {stats_data['total']}\n\n"
        f"✅ مجاز: {stats_data['allowed']}\n"
        f"🚫 بن شده: {stats_data['banned']}\n"
        f"⚠️ محدود شده: {stats_data['rate_limited']}"
    )

    await update.message.reply_text(text)


async def ai_performance(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show AI performance statistics."""

    if not await check_admin(update):
        return

    from services.ai_stats_service import AIStatsService

    stats_data = AIStatsService().get_stats()

    text = (
        "📊 عملکرد هوش مصنوعی\n\n"
        f"💬 کل درخواست‌ها: {stats_data['total']}\n\n"
    )

    for provider in stats_data["providers"]:

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

    for item in stats_data["security"]:
        text += f"• {item[0]} : {item[1]}\n"

    await update.message.reply_text(text)


async def ban_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Ban a user."""

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text(
            "استفاده:\n"
            "/ban_user USER_ID"
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ USER_ID باید عدد باشد."
        )
        return

    if user_id <= 0:
        await update.message.reply_text(
            "❌ USER_ID نامعتبر است."
        )
        return

    ban_service.ban_user(
        user_id,
        "admin ban",
    )

    await update.message.reply_text(
        f"🚫 کاربر {user_id} مسدود شد."
    )


async def unban_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Unban a user."""

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text(
            "استفاده:\n"
            "/unban_user USER_ID"
        )
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ USER_ID باید عدد باشد."
        )
        return

    if user_id <= 0:
        await update.message.reply_text(
            "❌ USER_ID نامعتبر است."
        )
        return

    ban_service.unban_user(user_id)

    await update.message.reply_text(
        f"✅ کاربر {user_id} آزاد شد."
    )


async def banned_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show banned users."""

    if not await check_admin(update):
        return

    users = ban_service.get_banned_users()

    text = "🚫 کاربران مسدود شده:\n\n"

    if not users:
        text += "لیست خالی است."

    else:
        for index, user in enumerate(users, 1):
            text += (
                f"{index}. ID: {user[0]}\n"
                f"زمان: {user[1]}\n\n"
            )

    await update.message.reply_text(text)


async def blocked_attempts(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show blocked security attempts."""

    if not await check_admin(update):
        return

    requests = security_service.get_blocked_attempts()

    if not requests:
        await update.message.reply_text(
            "✅ تلاش مسدود شده‌ای وجود ندارد."
        )
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


async def approve_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Approve a payment and notify the user."""

    if not await check_admin(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ شماره پرداخت را وارد کنید.\n\n"
            "مثال:\n"
            "/approve 2"
        )
        return

    try:
        payment_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ شماره پرداخت باید عدد باشد."
        )
        return

    if payment_id <= 0:
        await update.message.reply_text(
            "❌ شماره پرداخت نامعتبر است."
        )
        return

    payment = payment_service.get_payment(payment_id)

    if not payment:
        await update.message.reply_text(
            "❌ پرداخت پیدا نشد."
        )
        return

    if payment[4] == "paid":
        await update.message.reply_text(
            "⚠️ این پرداخت قبلاً تأیید شده است."
        )
        return

    success = payment_service.approve_payment(payment_id)

    if not success:
        await update.message.reply_text(
            "❌ پرداخت تأیید نشد."
        )
        return

    user_id = payment[1]

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🎉 تبریک!\n\n"
                "⭐ اشتراک ویژه Aydin AI برای شما فعال شد.\n\n"
                "✅ اکنون به امکانات Premium دسترسی دارید."
            ),
        )
    except Exception:
        logging.exception(
            "Failed to notify user %s after payment approval",
            user_id,
        )

    await update.message.reply_text(
        "✅ پرداخت تأیید شد.\n"
        "⭐ اشتراک کاربر فعال شد."
    )
