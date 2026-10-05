"""Weather message handler."""

from telegram import Update
from telegram.ext import ContextTypes

from services.weather_service import WeatherService

weather_service = WeatherService()


async def handle_weather(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Handle weather city input."""

    city = update.message.text.strip()

    if city == "⛅ آب‌وهوا":
        await update.message.reply_text("⛅ لطفاً نام شهر خود را وارد کنید.")
        return

    weather = weather_service.get_weather(city)

    if not weather:
        await update.message.reply_text(
            "❌ شهر پیدا نشد. لطفاً نام شهر را دقیق وارد کنید."
        )
        return

    await update.message.reply_text(weather)

    context.user_data.pop("mode", None)
