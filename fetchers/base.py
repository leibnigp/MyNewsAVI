from abc import ABC, abstractmethod
from typing import Optional
from models import Source


class BaseFetcher(ABC):
    """Abstract base class for all fetchers."""

    @abstractmethod
    def fetch(self, source: Source) -> list[dict]:
        """
        Fetch articles from the source.
        Returns list of normalized article dicts:
        {url, title, summary_raw, content_raw, author, published_at}
        """

    def normalize(self, raw: dict) -> dict:
        """Normalize a raw article dict to standard fields."""
        return {
            "url": str(raw.get("url", "")).strip(),
            "title": str(raw.get("title", "")).strip(),
            "summary_raw": str(raw.get("summary_raw", raw.get("summary", ""))).strip() or None,
            "content_raw": str(raw.get("content_raw", raw.get("content", ""))).strip() or None,
            "author": str(raw.get("author", "")).strip() or None,
            "published_at": raw.get("published_at"),
        }
