"""Application configuration."""

import os

from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")

FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")