from models import Source

SEED_SOURCES = [
    # === RSS Feeds ===
    {
        "name": "Air Cargo News",
        "source_type": "rss",
        "url": "https://www.aircargonews.net/feed/",
        "config": "{}",
        "fetch_interval_minutes": 60,
    },
    {
        "name": "FreightWaves",
        "source_type": "rss",
        "url": "https://www.freightwaves.com/feed",
        "config": "{}",
        "fetch_interval_minutes": 60,
    },
    {
        "name": "FlightGlobal",
        "source_type": "rss",
        "url": "https://www.flightglobal.com/rss",
        "config": "{}",
        "fetch_interval_minutes": 60,
    },
    # Cargo Facts blocked (403), disabled
    {
        "name": "Cargo Facts",
        "source_type": "rss",
        "url": "https://cargofacts.com/feed/",
        "config": "{}",
        "fetch_interval_minutes": 60,
        "enabled": False,
    },
    # === NewsAPI (need API key, disabled by default) ===
    {
        "name": "NewsAPI - FedEx Routes",
        "source_type": "newsapi",
        "url": "https://newsapi.org/v2/everything",
        "config": '{"query": "FedEx new flight route OR intercontinental cargo", "api_key_env": "NEWSAPI_KEY", "language": "en", "page_size": 10}',
        "fetch_interval_minutes": 240,
        "enabled": False,
    },
    {
        "name": "NewsAPI - UPS Routes",
        "source_type": "newsapi",
        "url": "https://newsapi.org/v2/everything",
        "config": '{"query": "UPS international air cargo route OR freighter", "api_key_env": "NEWSAPI_KEY", "language": "en", "page_size": 10}',
        "fetch_interval_minutes": 240,
        "enabled": False,
    },
    {
        "name": "NewsAPI - Air Cargo Asia",
        "source_type": "newsapi",
        "url": "https://newsapi.org/v2/everything",
        "config": '{"query": "air cargo route expansion Asia FedEx UPS", "api_key_env": "NEWSAPI_KEY", "language": "en", "page_size": 10}',
        "fetch_interval_minutes": 240,
        "enabled": False,
    },
]


def seed_sources():
    """Insert seed sources into DB if the Source table is empty."""
    if Source.select().count() == 0:
        seen_names = set()
        for src in SEED_SOURCES:
            if src["name"] in seen_names:
                continue
            seen_names.add(src["name"])
            Source.create(
                name=src["name"],
                source_type=src["source_type"],
                url=src["url"],
                config=src.get("config", "{}"),
                fetch_interval_minutes=src.get("fetch_interval_minutes", 60),
                enabled=src.get("enabled", True),
            )
