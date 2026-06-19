import os
from urllib.parse import urljoin
from models import Source
from fetchers.rss_fetcher import RSSFetcher


class RSSHubFetcher(RSSFetcher):
    """RSSHub-based fetcher for WeChat/Xiaohongshu etc.

    Extends RSSFetcher — RSSHub generates standard RSS feeds from
    platforms that don't natively provide them.
    """

    def __init__(self):
        super().__init__()
        self.rsshub_base = os.getenv("RSSHUB_BASE_URL", "https://rsshub.app")

    def _resolve_url(self, source_url: str) -> str:
        if source_url.startswith("http"):
            return source_url
        return urljoin(self.rsshub_base, source_url.lstrip("/"))

    def fetch(self, source: Source) -> list[dict]:
        # Temporarily swap URL to resolved RSSHub URL
        original_url = source.url
        source.url = self._resolve_url(original_url)
        try:
            return super().fetch(source)
        finally:
            source.url = original_url
