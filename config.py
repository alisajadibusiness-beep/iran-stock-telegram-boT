import os


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_ID = os.getenv("ADMIN_ID", "").strip()

DATABASE_PATH = os.getenv(
    "DATABASE_PATH",
    "stocks.db"
)

PORT = int(os.getenv("PORT", "10000"))

MARKET_REFRESH_SECONDS = int(
    os.getenv("MARKET_REFRESH_SECONDS", "300")
)

SIGNAL_SCAN_SECONDS = int(
    os.getenv("SIGNAL_SCAN_SECONDS", "300")
)

APP_NAME = os.getenv(
    "APP_NAME",
    "Iran Stock Analyzer"
)

TIMEZONE = os.getenv(
    "TIMEZONE",
    "Asia/Tehran"
)
