import os
import json
import certifi
from datetime import datetime, timedelta
import httpx
from models import Source
from fetchers.base import BaseFetcher
from utils.date_utils import parse_date


class NewsAPIFetcher(BaseFetcher):
    """NewsAPI / Gnews keyword-based fetcher."""

    def __init__(self):
        self.client = httpx.Client(timeout=30.0, verify=certifi.where())

    def fetch(self, source: Source) -> list[dict]:
        articles = []
        try:
            config = json.loads(source.config or "{}")
            api_key_env = config.get("api_key_env", "NEWSAPI_KEY")
            api_key = os.getenv(api_key_env, "")
            if not api_key:
                return articles  # silently skip if no key configured

            from_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
            params = {
                "q": config.get("query", ""),
                "apiKey": api_key,
                "from": from_date,
                "sortBy": "publishedAt",
                "language": config.get("language", "en"),
                "pageSize": config.get("page_size", 10),
            }

            resp = self.client.get(source.url, params=params)
            resp.raise_for_status()
            data = resp.json()

            for item in data.get("articles", []):
                raw = {
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                    "summary_raw": item.get("description", ""),
                    "content_raw": item.get("content", ""),
                    "author": item.get("author", ""),
                    "published_at": parse_date(item.get("publishedAt")),
                }
                articles.append(self.normalize(raw))
        except Exception:
            pass
        return articles
