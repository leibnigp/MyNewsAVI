import datetime
import json
from flask import Blueprint, jsonify, request, render_template
from peewee import fn
from models import Article, RouteChange, Source, Notification
from scheduler import fetch_all

api_bp = Blueprint("api", __name__, url_prefix="/api")


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
