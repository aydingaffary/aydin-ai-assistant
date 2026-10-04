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

    city = update.message.text

    response = weather_service.get_weather(city)

    await update.message.reply_text(response)

    context.user_data.pop("mode", None)