import ssl
import certifi
import urllib.request
import feedparser
from models import Source
from fetchers.base import BaseFetcher
from utils.date_utils import parse_date


class RSSFetcher(BaseFetcher):
    """Generic RSS/Atom feed fetcher using feedparser."""

    def __init__(self):
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())

    def fetch(self, source: Source) -> list[dict]:
        articles = []
        try:
            req = urllib.request.Request(
                source.url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
            )
            with urllib.request.urlopen(req, context=self._ssl_context, timeout=30) as resp:
                raw_content = resp.read().decode("utf-8", errors="ignore")

            feed = feedparser.parse(raw_content)
            if not feed.entries:
                return articles

            for entry in feed.entries:
                raw = {
                    "url": entry.get("link", ""),
                    "title": entry.get("title", ""),
                    "summary_raw": entry.get("summary", entry.get("description", "")),
                    "author": entry.get("author", ""),
                    "published_at": parse_date(
                        entry.get("published") or entry.get("updated")
                    ),
                }
                articles.append(self.normalize(raw))
        except Exception:
            pass
        return articles
