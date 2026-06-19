import hashlib
import json
import re
from difflib import SequenceMatcher
from models import Article


def url_to_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()


def title_similarity(a: str, b: str) -> float:
    """Return similarity ratio between two titles (0-1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def find_duplicate(title: str, source_id: int, threshold: float = 0.85) -> bool:
    """Check if a similar article from the same source exists within 7 days."""
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    candidates = (
        Article.select()
        .where(
            (Article.source_id == source_id)
            & (Article.fetched_at >= week_ago)
        )
    )
    for article in candidates:
        if title_similarity(title, article.title) > threshold:
            return True
    return False


def extract_keywords(text: str, keyword_list: list[str]) -> list[str]:
    """Extract matching keywords from text."""
    if not text:
        return []
    text_lower = text.lower()
    return sorted({kw for kw in keyword_list if kw.lower() in text_lower})


def clean_html(raw_html: str) -> str:
    """Strip HTML tags from text."""
    clean = re.compile(r"<[^>]+>")
    return clean.sub("", raw_html or "")
