import json
import certifi
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup
from models import Source
from fetchers.base import BaseFetcher
from utils.date_utils import parse_date


class WebScraperFetcher(BaseFetcher):
    """Site-specific web scraper using BeautifulSoup."""

    def __init__(self):
        self.client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=30.0,
            follow_redirects=True,
            verify=certifi.where(),
        )

    def fetch(self, source: Source) -> list[dict]:
        articles = []
        try:
            config = json.loads(source.config or "{}")
            resp = self.client.get(source.url)
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "lxml")
            items = soup.select(config.get("article_selector", "article"))

            for item in items[:20]:
                try:
                    title_el = item.select_one(config.get("title_selector", "h2 a"))
                    if not title_el:
                        continue

                    href = title_el.get("href", "")
                    if href and not href.startswith("http"):
                        href = urljoin(source.url, href)

                    summary_el = item.select_one(config.get("summary_selector", "p"))
                    date_el = item.select_one(config.get("date_selector", "time"))

                    raw = {
                        "url": href,
                        "title": title_el.get_text(strip=True),
                        "summary_raw": summary_el.get_text(strip=True) if summary_el else "",
                        "author": "",
                        "published_at": parse_date(date_el.get_text(strip=True)) if date_el else None,
                    }
                    articles.append(self.normalize(raw))
                except Exception:
                    continue
        except Exception:
            pass
        return articles
