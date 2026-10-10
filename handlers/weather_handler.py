"""Weather message handler."""

from services.weather_service import WeatherService
from services.chat_state import get_member_state

weather_service = WeatherService()


async def handle_weather(update, context):
    if not update.message or not update.message.text:
        return

    city = update.message.text.strip()
    normalized = city.replace("\u200c", "").replace(" ", "").strip().casefold()

    if normalized in {
        "⛅آبوهوا", "⛅️آبوهوا", "آبوهوا", "هوا", "وضعیت هوا",
    }:
        await update.message.reply_text(
            "⛅ لطفاً نام شهر را وارد کنید؛ مثلاً تبریز یا تهران."
        )
        return

    weather = weather_service.get_weather(city)
    if not weather:
        await update.message.reply_text(
            "❌ شهر پیدا نشد. نام شهر را دقیق وارد کنید یا یک شهر دیگر بنویسید."
        )
        return

    await update.message.reply_text(weather)

    # Clear the correct state: per-member state in groups, user_data in private.
    state = get_member_state(update, context)
    if state.get("mode") == "weather":
        state.pop("mode", None)
