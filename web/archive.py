from flask import Blueprint, render_template, request
from models import Article
from peewee import fn

archive_bp = Blueprint("archive", __name__)


@archive_bp.route("/archive")
def archive():
    query = Article.select().order_by(Article.published_at.desc())

    q = request.args.get("q", "").strip()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()
    carrier = request.args.get("carrier", "").strip()
    page = request.args.get("page", 1, type=int)
    per_page = 20

    if q:
        query = query.where(
            (Article.title.contains(q))
            | (Article.summary_raw.contains(q))
            | (Article.ai_summary_cn.contains(q))
        )
    if date_from:
        query = query.where(Article.published_at >= date_from)
    if date_to:
        query = query.where(Article.published_at <= date_to + " 23:59:59")
    if carrier:
        query = query.where(Article.carrier == carrier)

    total = query.count()
    articles_list = list(query.paginate(page, per_page))
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        "archive.html",
        articles=articles_list,
        page=page,
        total_pages=total_pages,
        total=total,
        q=q,
        date_from=date_from,
        date_to=date_to,
        carrier=carrier,
    )
