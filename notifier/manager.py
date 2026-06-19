import datetime
from models import Article, RouteChange, Notification
from notifier.desktop import send_desktop
from notifier.email_sender import send_email, build_route_alert_html

# Airport code to continent mapping (simplified)
NORTH_AMERICA_CODES = {"MEM", "SDF", "ANC", "EWR", "LAX", "ORD", "MIA", "JFK", "DFW", "IAH", "CVG", "PHL", "OAK"}
EUROPE_CODES = {"CDG", "LHR", "LEJ", "CGN", "AMS", "FRA", "MUC", "MAD", "STN", "LGG", "BRU", "DUB"}
ASIA_PACIFIC_CODES = {"SZX", "CAN", "PVG", "PEK", "HKG", "NRT", "KIX", "ICN", "SIN", "BKK", "TPE", "KUL", "MNL", "SYD", "MEL"}
MIDDLE_EAST_CODES = {"DXB", "DOH", "AUH", "JED", "RUH", "BAH"}
LATIN_AMERICA_CODES = {"MEX", "GRU", "VCP", "BOG", "LIM", "SCL", "EZE"}


def _get_continent(code: str) -> str:
    code = code.upper().strip()
    if code in NORTH_AMERICA_CODES:
        return "North America"
    if code in EUROPE_CODES:
        return "Europe"
    if code in ASIA_PACIFIC_CODES:
        return "Asia-Pacific"
    if code in MIDDLE_EAST_CODES:
        return "Middle East"
    if code in LATIN_AMERICA_CODES:
        return "Latin America"
    return "Other"


def _is_intercontinental(origin: str, dest: str) -> bool:
    c1 = _get_continent(origin)
    c2 = _get_continent(dest)
    if c1 == "Other" or c2 == "Other":
        return False
    return c1 != c2


def check_and_notify(article: Article):
    """Decide whether to send a notification based on extracted route changes."""
    routes = list(RouteChange.select().where(RouteChange.article == article))

    if not routes:
        return

    notify_routes = []
    notification_type = None

    for route in routes:
        if route.action == "new" and _is_intercontinental(route.origin, route.destination):
            notify_routes.append(route)
            notification_type = "new_route"
        elif route.action in ("resumed", "suspended"):
            notify_routes.append(route)
            notification_type = "intercontinental_change"

    if not notify_routes:
        return

    # Build notification content
    carrier = article.carrier or "Unknown"
    first_route = notify_routes[0]

    if notification_type == "new_route":
        title = f"新洲际航线: {carrier} {first_route.origin}→{first_route.destination}"
    elif first_route.action == "resumed":
        title = f"航线恢复: {carrier} {first_route.origin}→{first_route.destination}"
    elif first_route.action == "suspended":
        title = f"航线停运: {carrier} {first_route.origin}→{first_route.destination}"
    else:
        title = f"航线变动: {carrier}"

    body_text = article.ai_summary_cn or article.title
    if len(body_text) > 200:
        body_text = body_text[:197] + "..."

    # Save notification record
    Notification.create(
        article=article,
        title=title,
        body=body_text,
        notification_type=notification_type,
        sent_at=datetime.datetime.now(),
    )

    # Send desktop notification (Mac only, best-effort)
    send_desktop(title, body_text)

    # Send email notification (for when user is at work on company PC)
    if notify_routes:
        html_body = build_route_alert_html(article, notify_routes)
        sent = send_email(f"[MyNewsAVI] {title}", html_body)
        if sent:
            print(f"[Email] Alert sent: {title}", flush=True)


def send_daily_digest():
    """Send a daily digest summarizing today's activity."""
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    new_count = Article.select().where(Article.fetched_at >= today_start).count()
    route_count = RouteChange.select().where(RouteChange.created_at >= today_start).count()

    if new_count == 0 and route_count == 0:
        return

    title = "MyNewsAVI 日报"
    body = f"今日新增 {new_count} 篇文章，检测到 {route_count} 条路线变更"

    Notification.create(
        article=None,
        title=title,
        body=body,
        notification_type="daily_digest",
        sent_at=datetime.datetime.now(),
    )

    send_desktop(title, body)

    # Email the daily digest too
    digest_html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        <div style="background:#1e40af;color:white;padding:16px 24px;">
            <h2 style="margin:0;font-size:18px;">MyNewsAVI · 每日日报</h2>
        </div>
        <div style="padding:24px;">
            <table style="width:100%;border-collapse:collapse;font-size:14px;">
                <tr><td style="padding:12px;border-bottom:1px solid #eee;">今日新增文章</td><td style="padding:12px;border-bottom:1px solid #eee;font-weight:bold;color:#1e40af;">{new_count} 篇</td></tr>
                <tr><td style="padding:12px;border-bottom:1px solid #eee;">检测到路线变更</td><td style="padding:12px;border-bottom:1px solid #eee;font-weight:bold;color:#059669;">{route_count} 条</td></tr>
                <tr><td style="padding:12px;border-bottom:1px solid #eee;">待AI分析</td><td style="padding:12px;border-bottom:1px solid #eee;font-weight:bold;color:#d97706;">{Article.select().where(Article.analysis_status == "pending").count()} 篇</td></tr>
            </table>
            <p style="color:#9ca3af;font-size:12px;margin-top:16px;">此邮件由 MyNewsAVI 自动发送 · 详情请返回 Mac 查看完整 Dashboard</p>
        </div>
    </div>"""
    send_email("[MyNewsAVI] 每日日报", digest_html)
