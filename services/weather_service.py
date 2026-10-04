"""Weather service for retrieving current and forecast data."""

from datetime import datetime

import requests


class WeatherService:
    """Handle weather information."""

    GEOCODING_URL = "https://nominatim.openstreetmap.org/search"

    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

    def get_coordinates(self, city: str) -> dict | None:
        """Find city coordinates using Nominatim."""

        response = requests.get(
            self.GEOCODING_URL,
            params={
                "q": city,
                "format": "json",
                "limit": 1,
            },
            headers={"User-Agent": "Aydin-AI-Assistant/1.0"},
            timeout=10,
        )

        data = response.json()

        if not data:
            return None

        result = data[0]

        return {
            "name": result.get("display_name", city).split(",")[0],
            "country": ("ایران" if "ایران" in result.get("display_name", "") else ""),
            "latitude": float(result["lat"]),
            "longitude": float(result["lon"]),
        }

    def get_weather_description(self, code: int) -> str:
        """Convert weather code to Persian text."""

        descriptions = {
            0: "☀️ آفتابی",
            1: "🌤 کمی ابری",
            2: "⛅ نیمه ابری",
            3: "☁️ ابری",
            45: "🌫 مه‌آلود",
            48: "🌫 مه یخ‌زده",
            51: "🌧 باران سبک",
            53: "🌧 بارانی",
            55: "🌧 باران شدید",
            61: "🌧 بارانی",
            63: "🌧 بارانی",
            65: "🌧 باران شدید",
            71: "❄️ برفی",
            73: "❄️ برفی",
            75: "❄️ برف شدید",
            80: "🌦 رگبار",
            81: "🌦 رگبار",
            82: "⛈ رگبار شدید",
            95: "⛈ طوفانی",
            96: "⛈ طوفان با تگرگ",
            99: "⛈ طوفان شدید",
        }

        return descriptions.get(code, "🌍 نامشخص")

    def get_day_name(self, date: str) -> str:
        """Convert date to Persian weekday name."""

        days = {
            0: "دوشنبه",
            1: "سه‌شنبه",
            2: "چهارشنبه",
            3: "پنج‌شنبه",
            4: "جمعه",
            5: "شنبه",
            6: "یکشنبه",
        }

        weekday = datetime.fromisoformat(date).weekday()

        return days[weekday]

    def get_weather(self, city: str) -> str:
        """Get weather information."""

        location = self.get_coordinates(city)

        if not location:
            return "شهر پیدا نشد."

        response = requests.get(
            self.WEATHER_URL,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": ("temperature_2m," "windspeed_10m," "weather_code"),
                "daily": ("temperature_2m_max," "temperature_2m_min," "weather_code"),
                "forecast_days": 4,
                "timezone": "auto",
            },
            timeout=10,
        )

        data = response.json()

        current = data["current"]
        daily = data["daily"]

        location_text = location["name"]

        if location["country"]:
            location_text += f", {location['country']}"

        current_description = self.get_weather_description(current["weather_code"])

        message = (
            f"🌍 {location_text}\n\n"
            f"{current_description}\n"
            f"🌡 دمای فعلی: {current['temperature_2m']}°C\n"
            f"💨 سرعت باد: {current['windspeed_10m']} km/h\n"
        )

        message += "\n📅 پیش‌بینی ۳ روز آینده:\n"

        for i in range(1, 4):
            day_name = self.get_day_name(daily["time"][i])

            description = self.get_weather_description(daily["weather_code"][i])

            message += (
                f"\n{day_name}:\n"
                f"{description}\n"
                f"⬆️ {daily['temperature_2m_max'][i]}°C "
                f"⬇️ {daily['temperature_2m_min'][i]}°C\n"
            )

        return message
