from flask import Blueprint, render_template
from models import Article, RouteChange
from utils.date_utils import relative_time

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    latest_articles = (
        Article.select()
        .order_by(Article.fetched_at.desc())
        .limit(20)
    )
    return render_template("index.html", articles=latest_articles)


@main_bp.route("/article/<int:article_id>")
def article_detail(article_id):
    article = Article.get_or_none(article_id)
    if not article:
        return "Article not found", 404

    route_changes = list(
        RouteChange.select().where(RouteChange.article == article)
    )

    from models import Source
    source = Source.get_or_none(article.source_id)

    return render_template(
        "article_detail.html",
        article=article,
        source=source,
        route_changes=route_changes,
    )
