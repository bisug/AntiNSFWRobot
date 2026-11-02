import os
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")

    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "5432")) if os.getenv("DB_PORT") else 5432
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    DB_SSLMODE = os.getenv("DB_SSLMODE", "prefer")
    DB_MIN_CONNECTIONS = int(os.getenv("DB_MIN_CONNECTIONS", "1"))
    DB_MAX_CONNECTIONS = int(os.getenv("DB_MAX_CONNECTIONS", "10"))

    if DATABASE_URL:
        _parsed = urlparse(DATABASE_URL)
        DB_HOST = DB_HOST or _parsed.hostname
        DB_PORT = int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else (_parsed.port or 5432)
        DB_USER = DB_USER or _parsed.username
        DB_PASSWORD = DB_PASSWORD or _parsed.password
        DB_NAME = DB_NAME or (_parsed.path.lstrip("/") if _parsed.path else None)
