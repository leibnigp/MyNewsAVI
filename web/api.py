import datetime
import json
import os
import hashlib
from flask import Blueprint, jsonify, request, render_template
from peewee import fn
from models import Article, RouteChange, Source, Notification
from scheduler import fetch_all
from config import BASE_DIR

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Cache for intercontinental summary
_SUMMARY_CACHE_PATH = os.path.join(BASE_DIR, "data", "intercontinental_summary.json")


def _get_summary_cache():
    if os.path.exists(_SUMMARY_CACHE_PATH):
        try:
            with open(_SUMMARY_CACHE_PATH, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return None


def _set_summary_cache(summary_text: str, article_ids: list):
    os.makedirs(os.path.dirname(_SUMMARY_CACHE_PATH), exist_ok=True)
    with open(_SUMMARY_CACHE_PATH, "w") as f:
        json.dump({
            "summary": summary_text,
            "article_ids": article_ids,
            "generated_at": datetime.datetime.now().isoformat(),
        }, f, ensure_ascii=False)


@api_bp.route("/articles")
def articles():
    """Return filtered article list as HTML partial (for HTMX)."""
    query = Article.select().order_by(Article.fetched_at.desc())

    carrier = request.args.get("carrier", "").strip()
    region = request.args.get("region", "").strip()
    route_type = request.args.get("route_type", "").strip()
    keyword = request.args.get("keyword", "").strip()
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if carrier:
        query = query.where(Article.carrier == carrier)
    if region:
        query = query.where(Article.region == region)
    if route_type:
        query = query.where(Article.route_type == route_type)
    if keyword:
        query = query.where(
            (Article.title.contains(keyword))
            | (Article.summary_raw.contains(keyword))
            | (Article.keywords.contains(keyword))
        )
    if q:
        query = query.where(
            (Article.title.contains(q))
            | (Article.summary_raw.contains(q))
            | (Article.ai_summary_cn.contains(q))
        )

    total = query.count()
    articles_list = list(query.paginate(page, per_page))

    return render_template(
        "partials/article_list.html",
        articles=articles_list,
        page=page,
        per_page=per_page,
        total=total,
    )


@api_bp.route("/refresh", methods=["POST"])
def refresh():
    """Manually trigger a fetch cycle for all sources."""
    try:
        fetch_all()
        return jsonify({"status": "ok", "message": "Fetch cycle completed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@api_bp.route("/stats")
def stats():
    """Dashboard stats."""
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)

    total = Article.select().count()
    new_today = Article.select().where(Article.fetched_at >= today).count()
    route_changes_this_week = RouteChange.select().where(
        RouteChange.created_at >= week_ago
    ).count()
    pending = Article.select().where(Article.analysis_status == "pending").count()
    unread_notifications = Notification.select().where(
        Notification.is_read == False
    ).count()

    return jsonify({
        "total_articles": total,
        "new_today": new_today,
        "route_changes_this_week": route_changes_this_week,
        "pending_analysis": pending,
        "unread_notifications": unread_notifications,
    })


@api_bp.route("/articles/<int:article_id>/flag", methods=["PUT"])
def toggle_flag(article_id):
    article = Article.get_or_none(article_id)
    if not article:
        return jsonify({"status": "error", "message": "Not found"}), 404
    article.is_flagged = not article.is_flagged
    article.save()
    return jsonify({"status": "ok", "is_flagged": article.is_flagged})


@api_bp.route("/articles/<int:article_id>", methods=["PATCH"])
def mark_read(article_id):
    article = Article.get_or_none(article_id)
    if not article:
        return jsonify({"status": "error", "message": "Not found"}), 404
    article.is_read = True
    article.save()
    return jsonify({"status": "ok"})


@api_bp.route("/analyze/<int:article_id>", methods=["POST"])
def analyze_single(article_id):
    article = Article.get_or_none(article_id)
    if not article:
        return jsonify({"status": "error", "message": "Not found"}), 404
    try:
        from analyzer.pipeline import process_article
        result = process_article(article)
        return jsonify(result)
    except ImportError:
        return jsonify({"status": "error", "message": "AI pipeline not available yet"}), 503


@api_bp.route("/analyze-batch", methods=["POST"])
def analyze_batch():
    try:
        from analyzer.pipeline import process_pending_articles
        count = process_pending_articles()
        return jsonify({"status": "ok", "processed_count": count})
    except ImportError:
        return jsonify({"status": "error", "message": "AI pipeline not available yet"}), 503


@api_bp.route("/intercontinental-summary")
def intercontinental_summary():
    """Return a Chinese summary of recent intercontinental route changes.
    Uses cache; add ?refresh=1 to regenerate via AI."""
    force_refresh = request.args.get("refresh") == "1"

    if not force_refresh:
        cached = _get_summary_cache()
        if cached:
            return jsonify({"summary": cached["summary"], "generated_at": cached["generated_at"], "cached": True})

    # Gather data: route changes + intercontinental/new_route articles from last 14 days
    recent = datetime.datetime.now() - datetime.timedelta(days=14)

    route_changes = list(
        RouteChange.select().where(RouteChange.created_at >= recent)
    )

    articles = list(
        Article.select().where(
            (Article.analysis_status == "done")
            & (Article.route_type.in_(["intercontinental", "new_route", "route_change"]))
            & (Article.fetched_at >= recent)
        ).order_by(Article.published_at.desc())
    )

    if not route_changes and not articles:
        summary = "过去两周暂无洲际航线变动记录。新的航线动态将在系统完成抓取与 AI 分析后自动更新。"
        _set_summary_cache(summary, [])
        return jsonify({"summary": summary, "generated_at": datetime.datetime.now().isoformat(), "cached": False})

    # Build a structured prompt for the AI
    lines = ["以下是最新的航空货运洲际航线变动数据，请生成一段 150 字以内的中文摘要，",
             "聚焦洲际航线的开通、停止、班期变更、服务范围扩大等变化。",
             "按时间倒序组织，先讲最新的变动，使用简洁专业的语言。\n"]

    if route_changes:
        lines.append("## 航线变更记录")
        for rc in route_changes[:20]:
            action_cn = {
                "new": "新开", "resumed": "恢复", "suspended": "暂停",
                "increased_frequency": "加密班次", "decreased_frequency": "减少班次",
                "aircraft_change": "机型更换"
            }.get(rc.action, rc.action)
            eff = rc.effective_date.strftime("%Y-%m-%d") if rc.effective_date else "日期待定"
            aircraft = f" ({rc.aircraft_type})" if rc.aircraft_type else ""
            lines.append(f"- {action_cn}: {rc.origin}→{rc.destination}{aircraft}，生效 {eff}")

    if articles:
        lines.append("\n## 相关文章摘要")
        for a in articles[:10]:
            summary = a.ai_summary_cn or a.title
            lines.append(f"- [{a.carrier or 'Unknown'}] {summary}")

    prompt = "\n".join(lines)

    try:
        from analyzer.client import get_client, get_model
        client = get_client()
        response = client.messages.create(
            model=get_model(),
            max_tokens=512,
            system="你是一个专业的航空货运行业分析师。请根据提供的航线变动数据生成简洁、专业的中文摘要。只输出摘要文本，不要加任何前缀、标题或 markdown。",
            messages=[{"role": "user", "content": prompt}],
            extra_headers={"anthropic-beta": "disable-thinking-2025-01-27"},
        )
        raw_text = ""
        for block in response.content:
            if getattr(block, "type", None) == "text":
                raw_text += block.text
        summary = raw_text.strip()
    except Exception as e:
        # Fallback: build summary from data without AI
        parts = []
        if route_changes:
            actions = {}
            for rc in route_changes:
                action_cn = {
                    "new": "新开", "resumed": "恢复", "suspended": "暂停",
                    "increased_frequency": "加密班次", "decreased_frequency": "减少班次",
                    "aircraft_change": "机型更换"
                }.get(rc.action, rc.action)
                key = f"{rc.origin}→{rc.destination}"
                actions[key] = action_cn
            for route, action in list(actions.items())[:5]:
                parts.append(f"{route} {action}")
        if articles:
            for a in articles[:3]:
                parts.append(a.ai_summary_cn or a.title)
        summary = "；".join(parts) if parts else "暂无航线变动"

    article_ids = [a.id for a in articles]
    _set_summary_cache(summary, article_ids)

    return jsonify({"summary": summary, "generated_at": datetime.datetime.now().isoformat(), "cached": False})
