from datetime import datetime
from dateutil import parser as dateutil_parser


def parse_date(value) -> datetime | None:
    """Parse a date string into a datetime object. Returns None on failure."""
    if value is None:
        return None
    try:
        return dateutil_parser.parse(str(value))
    except Exception:
        return None


def relative_time(dt: datetime) -> str:
    """Return a human-readable relative time string in Chinese."""
    if dt is None:
        return ""
    now = datetime.now()
    diff = now - dt.replace(tzinfo=None)

    if diff.days > 30:
        return f"{diff.days // 30} 个月前"
    elif diff.days > 0:
        return f"{diff.days} 天前"
    elif diff.seconds >= 3600:
        return f"{diff.seconds // 3600} 小时前"
    elif diff.seconds >= 60:
        return f"{diff.seconds // 60} 分钟前"
    else:
        return "刚刚"
