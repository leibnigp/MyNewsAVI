import json
import datetime
import time
from models import Article, RouteChange
from config import AI_BATCH_SIZE, AI_MAX_CONTENT_LENGTH
from analyzer.client import get_client, get_model
from analyzer.prompts import SYSTEM_PROMPT


def process_article(article: Article) -> dict:
    """Process a single article through the AI pipeline."""
    if article.analysis_status not in ("pending", "skipped"):
        return {"status": "skipped", "reason": f"already {article.analysis_status}"}

    article.analysis_status = "processing"
    article.save()

    try:
        client = get_client()

        content_parts = [
            article.content_raw or "",
            article.summary_raw or "",
        ]
        body = " ".join(p for p in content_parts if p)
        if not body:
            body = article.title

        user_message = f"Title: {article.title}\n\nContent: {body}"

        if len(user_message) > AI_MAX_CONTENT_LENGTH:
            user_message = user_message[:AI_MAX_CONTENT_LENGTH - 3] + "..."

        response = client.messages.create(
            model=get_model(),
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
            extra_headers={"anthropic-beta": "disable-thinking-2025-01-27"},
        )

        # Extract text from response — skip thinking blocks from DeepSeek
        raw_text = ""
        for block in response.content:
            if getattr(block, "type", None) == "text":
                raw_text += block.text
        raw_text = raw_text.strip()
        # Strip markdown code fences if present
        if raw_text.startswith("```"):
            lines = raw_text.split("\n")
            raw_text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        result = json.loads(raw_text)

        article.ai_summary_cn = result.get("summary_cn", "")
        article.carrier = result.get("carrier") or None
        article.route_type = _derive_route_type(result)
        article.region = result.get("regions", [None])[0] if result.get("regions") else None
        article.keywords = json.dumps(result.get("keywords_cn", []), ensure_ascii=False)
        article.analysis_status = "done"
        article.analyzed_at = datetime.datetime.now()
        article.save()

        # Create RouteChange records
        for route in result.get("routes", []):
            eff_date = None
            if route.get("effective_date"):
                try:
                    eff_date = datetime.datetime.strptime(route["effective_date"], "%Y-%m-%d")
                except (ValueError, TypeError):
                    pass

            RouteChange.create(
                article=article,
                origin=route.get("origin", "Unknown"),
                destination=route.get("destination", "Unknown"),
                action=route.get("action", ""),
                effective_date=eff_date,
                aircraft_type=route.get("aircraft_type"),
                confidence=float(route.get("confidence", 0.0)),
            )

        # Trigger notification check
        try:
            from notifier.manager import check_and_notify
            check_and_notify(article)
        except ImportError:
            pass

        return {"status": "done", "summary": article.ai_summary_cn}

    except json.JSONDecodeError as e:
        # One retry: set back to pending
        article.analysis_status = "pending"
        article.save()
        return {"status": "error", "reason": f"JSON parse error: {e}"}

    except Exception as e:
        article.analysis_status = "skipped"
        article.ai_summary_cn = f"[AI分析暂时不可用] {str(e)[:200]}"
        article.save()
        return {"status": "error", "reason": str(e)}


def process_pending_articles(limit: int = AI_BATCH_SIZE) -> int:
    """Process up to `limit` pending articles. Returns count processed."""
    articles = (
        Article.select()
        .where(Article.analysis_status == "pending")
        .limit(limit)
    )
    count = 0
    for article in articles:
        result = process_article(article)
        if result["status"] == "done":
            count += 1
        time.sleep(1)  # rate limiting between API calls
    return count


def _derive_route_type(result: dict) -> str | None:
    """Derive route_type from AI analysis result."""
    routes = result.get("routes", [])
    if not routes:
        return "general" if result.get("is_route_related") else None

    actions = {r.get("action") for r in routes}
    regions = result.get("regions", [])

    # Check if intercontinental
    if len(regions) >= 2:
        return "intercontinental"

    if "new" in actions:
        return "new_route"

    if any(a in actions for a in ("resumed", "suspended", "increased_frequency", "decreased_frequency", "aircraft_change")):
        return "route_change"

    return "general"
