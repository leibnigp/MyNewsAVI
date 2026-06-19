# News Portal Frontend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a magazine-style news portal at `/news` aggregating FedEx/UPS/DHL flight route news with hero, carrier columns, timeline, and route changes sections.

**Architecture:** New blueprint `web/news.py` serves both the page (`/news`) and HTMX API partials (`/api/news/*`). Template `news.html` extends base.html; four partials render each section. Existing filter/card templates updated for DHL carrier colors.

**Tech Stack:** Flask + Peewee + HTMX 2.0 + TailwindCSS (CDN)

---

### Task 1: Update existing UI for DHL carrier

**Files:**
- Modify: `templates/index.html:30-33`
- Modify: `templates/partials/article_card.html:9-17`
- Modify: `templates/base.html:28-33` (Tailwind config + nav colors)

- [ ] **Step 1: Add DHL color to Tailwind config and DHL nav link entry**

In `templates/base.html`, extend the tailwind config colors and add DHL-specific CSS variables via a style block. Also add DHL to the article_card carrier colors.

Open `templates/base.html`, after the tailwind config script (line ~21), add a style block for carrier-specific CSS:

```html
<style>
    .carrier-fedex { --carrier-color: #3b82f6; --carrier-bg: #dbeafe; --carrier-text: #1d4ed8; }
    .carrier-ups   { --carrier-color: #d4a574; --carrier-bg: #fef3c7; --carrier-text: #92400e; }
    .carrier-dhl   { --carrier-color: #c41e3a; --carrier-bg: #fde8ec; --carrier-text: #9f1239; }
    .carrier-both  { --carrier-color: #8b5cf6; --carrier-bg: #ede9fe; --carrier-text: #6d28d9; }
    .carrier-other { --carrier-color: #6b7280; --carrier-bg: #f3f4f6; --carrier-text: #374151; }
</style>
```

- [ ] **Step 2: Add DHL to index.html filter dropdown**

In `templates/index.html`, line 32 after the UPS option:

```html
<option value="DHL">DHL</option>
```

Insert after `<option value="UPS">UPS</option>`.

- [ ] **Step 3: Update article_card.html carrier badge colors for DHL**

In `templates/partials/article_card.html`, replace the carrier badge block (lines 9-17) with:

```html
{% if article.carrier %}
<span class="px-2 py-0.5 rounded-full font-medium text-xs
    {{ 'bg-blue-100 text-blue-700' if article.carrier == 'FedEx' else '' }}
    {{ 'bg-amber-100 text-amber-700' if article.carrier == 'UPS' else '' }}
    {{ 'bg-red-100 text-red-700' if article.carrier == 'DHL' else '' }}
    {{ 'bg-purple-100 text-purple-700' if article.carrier == 'Both' else '' }}
    {{ 'bg-gray-100 text-gray-600' if article.carrier not in ('FedEx', 'UPS', 'DHL', 'Both') else '' }}">
    {{ article.carrier }}
</span>
{% endif %}
```

---

### Task 2: Create news blueprint with page route and API endpoints

**Files:**
- Create: `web/news.py`

- [ ] **Step 1: Create web/news.py**

```python
from flask import Blueprint, render_template, request
from models import Article, RouteChange
from peewee import fn

news_bp = Blueprint("news", __name__)


def _get_featured_article():
    """Most recent article with route changes, fallback to most recent overall."""
    article = (
        Article.select()
        .join(RouteChange)
        .where(Article.analysis_status == "done")
        .order_by(Article.published_at.desc())
        .first()
    )
    if not article:
        article = Article.select().order_by(Article.published_at.desc()).first()
    return article


def _get_carrier_articles(carrier, limit=5):
    return list(
        Article.select()
        .where(Article.carrier == carrier)
        .order_by(Article.published_at.desc())
        .limit(limit)
    )


def _get_timeline_articles(page=1, per_page=15, carrier=None):
    query = Article.select().order_by(Article.published_at.desc())
    if carrier:
        query = query.where(Article.carrier == carrier)
    total = query.count()
    articles = list(query.paginate(page, per_page))
    return articles, total, page, per_page


def _get_recent_route_changes(limit=8):
    return list(
        RouteChange.select()
        .join(Article)
        .order_by(RouteChange.created_at.desc())
        .limit(limit)
    )


@news_bp.route("/news")
def news_page():
    featured = _get_featured_article()
    hero_routes = []
    if featured:
        hero_routes = list(
            RouteChange.select()
            .where(RouteChange.article == featured)
            .limit(2)
        )

    carrier_data = {
        "FedEx": _get_carrier_articles("FedEx"),
        "UPS": _get_carrier_articles("UPS"),
        "DHL": _get_carrier_articles("DHL"),
    }

    timeline_articles, total, page, per_page = _get_timeline_articles()
    route_changes = _get_recent_route_changes()

    return render_template(
        "news.html",
        featured=featured,
        hero_routes=hero_routes,
        carrier_data=carrier_data,
        timeline_articles=timeline_articles,
        timeline_total=total,
        timeline_page=page,
        timeline_per_page=per_page,
        route_changes=route_changes,
    )


# ── HTMX API partials ──────────────────────────────────────────

@news_bp.route("/api/news/hero")
def api_news_hero():
    featured = _get_featured_article()
    hero_routes = []
    if featured:
        hero_routes = list(
            RouteChange.select()
            .where(RouteChange.article == featured)
            .limit(2)
        )
    return render_template(
        "partials/news_hero.html",
        featured=featured,
        hero_routes=hero_routes,
    )


@news_bp.route("/api/news/carrier-columns")
def api_news_carrier_columns():
    carrier_data = {
        "FedEx": _get_carrier_articles("FedEx"),
        "UPS": _get_carrier_articles("UPS"),
        "DHL": _get_carrier_articles("DHL"),
    }
    return render_template(
        "partials/news_carrier_columns.html",
        carrier_data=carrier_data,
    )


@news_bp.route("/api/news/timeline")
def api_news_timeline():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 15, type=int)
    carrier = request.args.get("carrier", "").strip() or None
    articles, total, page, per_page = _get_timeline_articles(
        page=page, per_page=per_page, carrier=carrier
    )
    return render_template(
        "partials/news_timeline.html",
        articles=articles,
        total=total,
        page=page,
        per_page=per_page,
    )


@news_bp.route("/api/news/route-changes")
def api_news_route_changes():
    route_changes = _get_recent_route_changes()
    return render_template(
        "partials/news_route_changes.html",
        route_changes=route_changes,
    )
```

---

### Task 3: Create main news template

**Files:**
- Create: `templates/news.html`

- [ ] **Step 1: Create templates/news.html**

```html
{% extends "base.html" %}
{% block content %}
<div class="space-y-6">

    <!-- Section 1: Hero -->
    <div id="news-hero" hx-get="/api/news/hero" hx-trigger="every 300s">
        {% include "partials/news_hero.html" %}
    </div>

    <!-- Section 2: Three Carrier Columns -->
    <div id="news-carrier-columns" hx-get="/api/news/carrier-columns" hx-trigger="every 300s">
        {% include "partials/news_carrier_columns.html" %}
    </div>

    <!-- Section 3: Timeline Feed -->
    <div>
        <div class="flex items-center justify-between mb-3">
            <h3 class="text-lg font-bold text-gray-800">📰 最新资讯</h3>
            <div class="flex gap-2">
                <button class="text-xs px-3 py-1 rounded-full border border-gray-300 hover:bg-gray-100 {{ 'bg-gray-900 text-white' if not request.args.get('carrier') else '' }}"
                        hx-get="/api/news/timeline?page=1&per_page=15"
                        hx-target="#news-timeline-container">全部</button>
                <button class="text-xs px-3 py-1 rounded-full border border-gray-300 hover:bg-blue-50 text-blue-700"
                        hx-get="/api/news/timeline?page=1&per_page=15&carrier=FedEx"
                        hx-target="#news-timeline-container">FedEx</button>
                <button class="text-xs px-3 py-1 rounded-full border border-gray-300 hover:bg-amber-50 text-amber-700"
                        hx-get="/api/news/timeline?page=1&per_page=15&carrier=UPS"
                        hx-target="#news-timeline-container">UPS</button>
                <button class="text-xs px-3 py-1 rounded-full border border-gray-300 hover:bg-red-50 text-red-700"
                        hx-get="/api/news/timeline?page=1&per_page=15&carrier=DHL"
                        hx-target="#news-timeline-container">DHL</button>
            </div>
        </div>
        <div id="news-timeline-container">
            {% include "partials/news_timeline.html" %}
        </div>
    </div>

    <!-- Section 4: Route Changes Grid -->
    <div>
        <h3 class="text-lg font-bold text-gray-800 mb-3">🛫 航线变动速览</h3>
        <div id="news-route-changes" hx-get="/api/news/route-changes" hx-trigger="every 300s">
            {% include "partials/news_route_changes.html" %}
        </div>
    </div>

</div>
{% endblock %}
```

---

### Task 4: Create partial templates

**Files:**
- Create: `templates/partials/news_hero.html`
- Create: `templates/partials/news_carrier_columns.html`
- Create: `templates/partials/news_timeline.html`
- Create: `templates/partials/news_route_changes.html`

- [ ] **Step 1: Create templates/partials/news_hero.html**

```html
{% if featured %}
<div class="bg-gradient-to-br from-slate-900 via-slate-800 to-blue-900 rounded-xl p-6 text-white">
    <div class="flex flex-col lg:flex-row gap-6">
        <!-- Left: Featured article -->
        <div class="flex-1">
            <div class="flex flex-wrap gap-2 mb-3">
                {% if featured.carrier %}
                <span class="text-xs px-2 py-0.5 rounded-full font-medium
                    {{ 'bg-blue-500 text-white' if featured.carrier == 'FedEx' else '' }}
                    {{ 'bg-amber-500 text-white' if featured.carrier == 'UPS' else '' }}
                    {{ 'bg-red-500 text-white' if featured.carrier == 'DHL' else '' }}
                    {{ 'bg-purple-500 text-white' if featured.carrier == 'Both' else '' }}
                    {{ 'bg-gray-500 text-white' if featured.carrier not in ('FedEx', 'UPS', 'DHL', 'Both') else '' }}">
                    {{ featured.carrier }}
                </span>
                {% endif %}
                {% if featured.route_type %}
                {% set rt_labels = {'new_route': '新航线', 'route_change': '航线变更', 'intercontinental': '洲际航线', 'general': '综合新闻'} %}
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/20">{{ rt_labels.get(featured.route_type, featured.route_type) }}</span>
                {% endif %}
                {% if featured.region %}
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/20">{{ featured.region }}</span>
                {% endif %}
            </div>
            <a href="/article/{{ featured.id }}" class="text-xl lg:text-2xl font-bold leading-tight hover:underline">
                {{ featured.title }}
            </a>
            {% if featured.summary_raw %}
            <p class="mt-2 text-sm text-gray-300 leading-relaxed line-clamp-2">{{ featured.summary_raw }}</p>
            {% endif %}
            <div class="mt-3 flex items-center gap-4 text-xs text-gray-400">
                <span>{{ featured.published_at.strftime('%Y-%m-%d %H:%M') if featured.published_at else '未知日期' }}</span>
                {% if featured.source %}
                <span>来源: {{ featured.source.name }}</span>
                {% endif %}
            </div>
        </div>
        <!-- Right: Associated route changes -->
        {% if hero_routes %}
        <div class="lg:w-72 flex flex-col gap-2">
            {% for rc in hero_routes %}
            <div class="bg-white/10 rounded-lg p-3 backdrop-blur-sm">
                <div class="text-xs text-gray-400 mb-1">📊 航线变动</div>
                <div class="text-sm font-bold">{{ rc.origin }} → {{ rc.destination }}</div>
                <div class="text-xs text-gray-300 mt-0.5">
                    {% set action_labels = {'new': '新增', 'resumed': '恢复', 'suspended': '暂停', 'increased_freq': '增频', 'decreased_freq': '减频', 'aircraft_change': '机型变更'} %}
                    {{ action_labels.get(rc.action, rc.action) }}
                    {% if rc.aircraft_type %}· {{ rc.aircraft_type }}{% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</div>
{% else %}
<div class="bg-gradient-to-br from-slate-900 to-blue-900 rounded-xl p-8 text-center text-gray-400">
    <p class="text-lg">暂无头条新闻</p>
    <p class="text-sm mt-1">抓取数据后将自动展示最新航班动态</p>
</div>
{% endif %}
```

- [ ] **Step 2: Create templates/partials/news_carrier_columns.html**

```html
<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    {% for carrier, articles in carrier_data.items() %}
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <div class="px-4 py-3 font-bold text-sm text-white
            {{ 'bg-blue-500' if carrier == 'FedEx' else '' }}
            {{ 'bg-amber-500' if carrier == 'UPS' else '' }}
            {{ 'bg-red-600' if carrier == 'DHL' else '' }}">
            {{ carrier }}
        </div>
        <div class="divide-y divide-gray-100">
            {% if articles %}
                {% for article in articles %}
                <a href="/article/{{ article.id }}" class="block px-4 py-3 hover:bg-gray-50 transition-colors">
                    <div class="text-sm font-medium text-gray-800 line-clamp-2">{{ article.title }}</div>
                    <div class="text-xs text-gray-400 mt-1">
                        {{ article.published_at.strftime('%m-%d %H:%M') if article.published_at else '未知日期' }}
                        {% if article.region %}<span class="ml-2">{{ article.region }}</span>{% endif %}
                    </div>
                </a>
                {% endfor %}
            {% else %}
                <div class="px-4 py-6 text-center text-sm text-gray-400">暂无{{ carrier }}动态</div>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</div>
```

- [ ] **Step 3: Create templates/partials/news_timeline.html**

```html
{% if articles %}
<div class="bg-white rounded-lg shadow-sm border border-gray-200 divide-y divide-gray-100">
    {% for article in articles %}
    <a href="/article/{{ article.id }}" class="flex items-start gap-3 px-4 py-3 hover:bg-gray-50 transition-colors group">
        <!-- Carrier color bar -->
        <div class="w-1 self-stretch rounded-full flex-shrink-0
            {{ 'bg-blue-500' if article.carrier == 'FedEx' else '' }}
            {{ 'bg-amber-500' if article.carrier == 'UPS' else '' }}
            {{ 'bg-red-600' if article.carrier == 'DHL' else '' }}
            {{ 'bg-purple-500' if article.carrier == 'Both' else '' }}
            {{ 'bg-gray-400' if article.carrier not in ('FedEx', 'UPS', 'DHL', 'Both') else '' }}"
            style="min-height:2.5rem;"></div>
        <!-- Content -->
        <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-gray-800 group-hover:text-blue-600 transition-colors line-clamp-2">
                {{ article.title }}
            </div>
            <div class="flex items-center gap-2 mt-1 text-xs text-gray-400">
                <span>{{ article.published_at.strftime('%m-%d %H:%M') if article.published_at else '未知' }}</span>
                {% if article.carrier %}<span>{{ article.carrier }}</span>{% endif %}
                {% if article.region %}<span>{{ article.region }}</span>{% endif %}
            </div>
        </div>
        <!-- Route type badge -->
        {% if article.route_type %}
        {% set rt_labels = {'new_route': '新航线', 'route_change': '航线变更', 'intercontinental': '洲际航线', 'general': '综合'} %}
        {% set rt_color = {'new_route': 'bg-green-100 text-green-700', 'route_change': 'bg-yellow-100 text-yellow-700', 'intercontinental': 'bg-orange-100 text-orange-700', 'general': 'bg-gray-100 text-gray-600'} %}
        <span class="text-xs px-2 py-0.5 rounded-full flex-shrink-0 {{ rt_color.get(article.route_type, 'bg-gray-100 text-gray-600') }}">
            {{ rt_labels.get(article.route_type, article.route_type) }}
        </span>
        {% endif %}
    </a>
    {% endfor %}
</div>

<!-- Pagination -->
{% if total > per_page %}
<div class="flex justify-center items-center gap-2 mt-4 text-sm">
    {% if page > 1 %}
    <button class="px-4 py-1.5 border rounded-md hover:bg-gray-100"
            hx-get="/api/news/timeline?page={{ page - 1 }}&per_page={{ per_page }}{% if request.args.get('carrier') %}&carrier={{ request.args.get('carrier') }}{% endif %}"
            hx-target="#news-timeline-container"
            hx-swap="outerHTML">
        上一页
    </button>
    {% endif %}
    <span class="px-3 py-1.5 text-gray-500">第 {{ page }} 页 / 共 {{ (total + per_page - 1) // per_page }} 页</span>
    {% if page * per_page < total %}
    <button class="px-4 py-1.5 border rounded-md hover:bg-gray-100"
            hx-get="/api/news/timeline?page={{ page + 1 }}&per_page={{ per_page }}{% if request.args.get('carrier') %}&carrier={{ request.args.get('carrier') }}{% endif %}"
            hx-target="#news-timeline-container"
            hx-swap="outerHTML">
        下一页
    </button>
    {% endif %}
</div>
{% endif %}

{% else %}
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center text-gray-400">
    <p class="text-lg">暂无新闻</p>
    <p class="text-sm mt-1">尝试手动刷新或等待定时抓取</p>
</div>
{% endif %}
```

- [ ] **Step 4: Create templates/partials/news_route_changes.html**

```html
{% if route_changes %}
<div class="grid grid-cols-1 md:grid-cols-2 gap-3">
    {% for rc in route_changes %}
    {% set action_icons = {'new': '✈', 'resumed': '↗', 'suspended': '⏸', 'increased_freq': '↗', 'decreased_freq': '↘', 'aircraft_change': '🔄'} %}
    {% set action_labels = {'new': '新航线', 'resumed': '恢复', 'suspended': '暂停', 'increased_freq': '增频', 'decreased_freq': '减频', 'aircraft_change': '机型变更'} %}
    {% set action_colors = {'new': 'bg-green-50 text-green-700 border-green-200', 'resumed': 'bg-blue-50 text-blue-700 border-blue-200', 'suspended': 'bg-pink-50 text-pink-700 border-pink-200', 'increased_freq': 'bg-yellow-50 text-yellow-700 border-yellow-200', 'decreased_freq': 'bg-orange-50 text-orange-700 border-orange-200', 'aircraft_change': 'bg-indigo-50 text-indigo-700 border-indigo-200'} %}
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex items-center gap-3 hover:shadow-md transition-shadow">
        <div class="w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0
            {{ action_colors.get(rc.action, 'bg-gray-50 text-gray-600 border-gray-200') }} border">
            {{ action_icons.get(rc.action, '📌') }}
        </div>
        <div class="flex-1 min-w-0">
            <div class="text-sm font-semibold text-gray-800">
                {{ rc.origin }} → {{ rc.destination }}
            </div>
            <div class="text-xs text-gray-500 mt-0.5">
                {{ action_labels.get(rc.action, rc.action) }}
                {% if rc.aircraft_type %}· {{ rc.aircraft_type }}{% endif %}
                {% if rc.article and rc.article.carrier %}
                · <span class="font-medium
                    {{ 'text-blue-600' if rc.article.carrier == 'FedEx' else '' }}
                    {{ 'text-amber-600' if rc.article.carrier == 'UPS' else '' }}
                    {{ 'text-red-600' if rc.article.carrier == 'DHL' else '' }}">
                    {{ rc.article.carrier }}
                </span>
                {% endif %}
            </div>
        </div>
        <span class="text-xs px-2 py-0.5 rounded-full border flex-shrink-0 {{ action_colors.get(rc.action, 'bg-gray-50 text-gray-600 border-gray-200') }}">
            {{ action_labels.get(rc.action, rc.action) }}
        </span>
    </div>
    {% endfor %}
</div>
{% else %}
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8 text-center text-gray-400">
    <p>暂无航线变动记录</p>
</div>
{% endif %}
```

---

### Task 5: Register news blueprint in app.py

**Files:**
- Modify: `app.py:19-23`

- [ ] **Step 1: Register the news blueprint**

In `app.py`, after line 22 (`from web.reference import reference_bp`), add:

```python
from web.news import news_bp
```

And after `app.register_blueprint(reference_bp)` (line 23), add:

```python
app.register_blueprint(news_bp)
```

---

### Task 6: Add navigation link in base.html

**Files:**
- Modify: `templates/base.html:33`

- [ ] **Step 1: Add news portal nav link**

In `templates/base.html`, after the "航线版图" nav link (line 35), add:

```html
<a href="/news" class="text-sm font-medium text-gray-700 hover:text-brand-600 px-2 py-1 rounded-md {{ 'bg-brand-50 text-brand-700' if request.path == '/news' else '' }}">新闻门户</a>
```

Also update the footer text from "FedEx / UPS" to "FedEx / UPS / DHL":

```html
MyNewsAVI — 航空物流航线动态追踪 · FedEx / UPS / DHL
```

---

### Task 7: Add DHL news source to database

**Files:**
- Modify: `fetchers/registry.py` (or add via Python one-liner)

- [ ] **Step 1: Insert DHL news sources**

Run a script to add DHL news sources:

```bash
python3 -c "
from models import init_db, Source
db = init_db()
Source.get_or_create(
    name='NewsAPI - DHL Routes',
    defaults={
        'source_type': 'newsapi',
        'url': 'https://newsapi.org/v2/everything?q=DHL+aviation+cargo+routes',
        'enabled': True,
        'fetch_interval_minutes': 120,
    }
)
Source.get_or_create(
    name='NewsAPI - DHL Express',
    defaults={
        'source_type': 'newsapi',
        'url': 'https://newsapi.org/v2/everything?q=DHL+Express+air+cargo',
        'enabled': True,
        'fetch_interval_minutes': 120,
    }
)
print('DHL sources added')
"
```

- [ ] **Step 2: Verify the app starts**

```bash
cd /Users/guopenglin/Desktop/GuopengClaude/MyNewsAVI && python3 -c "from app import create_app; app = create_app(); print('App created OK, routes:'); [print(f'  {r.rule}') for r in app.url_map.iter_rules()]"
```

Expected: `/news`, `/api/news/hero`, `/api/news/carrier-columns`, `/api/news/timeline`, `/api/news/route-changes` all appear in route list.

---

### Task 8: Start dev server and verify

- [ ] **Step 1: Start the Flask dev server**

```bash
cd /Users/guopenglin/Desktop/GuopengClaude/MyNewsAVI && python3 app.py
```

- [ ] **Step 2: Verify in browser**

Open `http://localhost:8080/news` and confirm:
- Hero section renders (or shows empty state)
- Three carrier columns appear (FedEx blue, UPS gold, DHL red)
- Timeline feed lists articles
- Route changes grid shows cards
- Navigation link "新闻门户" works
- HTMX auto-refresh works on sections
- Filter tabs (全部/FedEx/UPS/DHL) filter the timeline
