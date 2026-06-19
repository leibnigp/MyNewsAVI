import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from config import (
    FETCH_CRON_HOUR, FETCH_CRON_MINUTE,
    AI_ANALYSIS_CRON_HOUR, AI_ANALYSIS_CRON_MINUTE,
    FETCH_ON_STARTUP, TRACKED_KEYWORDS,
)
from models import Source, Article, url_to_hash
from utils.text_utils import extract_keywords, find_duplicate

scheduler = BackgroundScheduler()

# Import fetcher classes
from fetchers.rss_fetcher import RSSFetcher
from fetchers.web_scraper import WebScraperFetcher
from fetchers.newsapi_fetcher import NewsAPIFetcher
from fetchers.rsshub_fetcher import RSSHubFetcher

_rss_fetcher = RSSFetcher()
_scraper_fetcher = WebScraperFetcher()
_newsapi_fetcher = NewsAPIFetcher()
_rsshub_fetcher = RSSHubFetcher()


def _get_fetcher(source_type: str):
    return {
        "rss": _rss_fetcher,
        "scraper": _scraper_fetcher,
        "newsapi": _newsapi_fetcher,
        "rsshub": _rsshub_fetcher,
    }.get(source_type)


def fetch_source(source_id: int):
    """Fetch articles from a single source and insert new ones."""
    try:
        source = Source.get_by_id(source_id)
    except Source.DoesNotExist:
        return

    fetcher = _get_fetcher(source.source_type)
    if not fetcher:
        return

    articles = fetcher.fetch(source)
    new_count = 0

    for article in articles:
        url = article.get("url", "")
        if not url or not article.get("title"):
            continue

        url_hash = url_to_hash(url)

        if Article.select().where(Article.url_hash == url_hash).exists():
            continue

        if find_duplicate(article["title"], source.id):
            continue

        text = f"{article['title']} {article.get('summary_raw', '') or ''}"
        kw_list = extract_keywords(text, TRACKED_KEYWORDS)

        try:
            Article.create(
                source=source,
                url=url,
                url_hash=url_hash,
                title=article["title"],
                summary_raw=article.get("summary_raw"),
                content_raw=article.get("content_raw"),
                author=article.get("author"),
                published_at=article.get("published_at"),
                analysis_status="pending",
                keywords=str(kw_list) if kw_list else None,
            )
            new_count += 1
        except Exception:
            continue

    source.last_fetched_at = datetime.datetime.now()
    source.save()

    if new_count > 0:
        print(f"[Fetcher] {source.name}: {new_count} new articles", flush=True)


def fetch_all():
    """Fetch from all enabled sources."""
    for source in Source.select().where(Source.enabled == True):
        fetch_source(source.id)


def start_scheduler():
    """Start all background jobs (cron-based, daily)."""
    if scheduler.running:
        return

    from fetchers.registry import seed_sources
    seed_sources()

    # All fetches: once per day at configured time (default 21:00)
    scheduler.add_job(
        fetch_all, "cron",
        hour=FETCH_CRON_HOUR, minute=FETCH_CRON_MINUTE,
        id="fetch_all_daily"
    )

    # AI analysis: 5 minutes after fetch
    from analyzer.pipeline import process_pending_articles
    scheduler.add_job(
        process_pending_articles, "cron",
        hour=AI_ANALYSIS_CRON_HOUR, minute=AI_ANALYSIS_CRON_MINUTE,
        id="ai_analysis_daily"
    )

    # Daily digest email: 5 minutes after AI analysis (21:10)
    digest_minute = (AI_ANALYSIS_CRON_MINUTE + 5) % 60
    digest_hour = AI_ANALYSIS_CRON_HOUR + (1 if AI_ANALYSIS_CRON_MINUTE + 5 >= 60 else 0)
    from notifier.manager import send_daily_digest
    scheduler.add_job(
        send_daily_digest, "cron",
        hour=digest_hour % 24, minute=digest_minute,
        id="daily_digest"
    )

    scheduler.start()
    print(f"[Scheduler] Daily fetch at {FETCH_CRON_HOUR:02d}:{FETCH_CRON_MINUTE:02d}, "
          f"AI at {AI_ANALYSIS_CRON_HOUR:02d}:{AI_ANALYSIS_CRON_MINUTE:02d}, "
          f"digest at {digest_hour % 24:02d}:{digest_minute:02d}", flush=True)

    # Also run on startup (when you open the lid and start the app)
    if FETCH_ON_STARTUP:
        scheduler.add_job(fetch_all, id="fetch_startup")
        print("[Scheduler] Startup fetch triggered", flush=True)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
