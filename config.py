import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_PATH = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "data", "mynewsavi.db"))

ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic")
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "deepseek-v4-pro[1m]")

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "")
RSSHUB_BASE_URL = os.getenv("RSSHUB_BASE_URL", "https://rsshub.app")

FETCH_ON_STARTUP = os.getenv("FETCH_ON_STARTUP", "true").lower() == "true"

# Cron-based: run once per day at 21:00 (when you're home and Mac is open)
FETCH_CRON_HOUR = int(os.getenv("FETCH_CRON_HOUR", "21"))
FETCH_CRON_MINUTE = int(os.getenv("FETCH_CRON_MINUTE", "0"))

# AI analysis runs 5 minutes after fetch
AI_ANALYSIS_CRON_HOUR = int(os.getenv("AI_ANALYSIS_CRON_HOUR", "21"))
AI_ANALYSIS_CRON_MINUTE = int(os.getenv("AI_ANALYSIS_CRON_MINUTE", "5"))

# AI analysis
AI_BATCH_SIZE = 5
AI_MAX_CONTENT_LENGTH = 4000

# Tracked keywords for auto-tagging
TRACKED_KEYWORDS = [
    "Guangzhou", "Shenzhen", "Shanghai", "Hong Kong", "Beijing",
    "Memphis", "Louisville", "Cologne", "Dubai", "Singapore",
    "767", "777", "747", "A330", "A300",
    "new route", "intercontinental", "transpacific", "transatlantic",
    "e-commerce", "capacity increase", "freighter",
]
