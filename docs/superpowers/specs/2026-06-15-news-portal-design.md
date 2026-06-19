# News Portal Frontend — Design Spec

**Date:** 2026-06-15
**Status:** approved

## Overview

Add a magazine-style news portal page (`/news`) to MyNewsAVI, aggregating flight route news from FedEx, UPS, and DHL. The page follows a Bloomberg/Reuters-style layout with a hero section, carrier columns, timeline feed, and route change cards.

## Architecture

- **New Blueprint:** `web/news.py` — `news_bp` at `/news`
- **New Template:** `templates/news.html` — extends `base.html`
- **New API Endpoints:** `/api/news/*` — returns HTML partials for each section (HTMX pattern)
- **New Partials:** `templates/partials/news_*.html` — reusable components (hero, carrier columns, timeline items, route cards)
- Register blueprint in `app.py`

## Page Layout (Four Sections)

### Section 1: Hero / 头条新闻
- Dark gradient background, full-width
- Left: featured article (latest or most important) — carrier badge, route type badge, title, summary, time + source
- Right: top 2 route changes associated with the featured article (aircraft, frequency, action)
- Updated on page load, can be refreshed

### Section 2: Three Carrier Columns / 三大承运人最新动态
- FedEx (blue #3b82f6), UPS (gold #d4a574), DHL (red #c41e3a)
- Each column shows the 5 most recent articles for that carrier
- Title links to article detail page

### Section 3: Timeline Feed / 最新资讯时间线
- All carriers mixed, sorted by published_at desc
- Each item: carrier color bar, title, time ago, region, route type badge
- Supports "load more" pagination (HTMX)

### Section 4: Route Changes Grid / 航线变动速览
- 2-column grid of route change cards
- Each card: icon + action type, origin → destination, carrier tag, change detail, action badge
- Sourced from `RouteChange` model, most recent first

## Carrier Colors

| Carrier | Primary | Light |
|---------|---------|-------|
| FedEx   | #3b82f6 | #dbeafe |
| UPS     | #d4a574 | #fef3c7 |
| DHL     | #c41e3a | #fde8ec |

## Data Model

- `Article.carrier` field already supports arbitrary strings — add "DHL" value
- No model changes needed; the carrier field is a free-text CharField

## DHL News Sources

New fetcher sources for DHL:
- NewsAPI query for "DHL aviation cargo routes"
- Additional RSS feeds (Air Cargo News already covers DHL topics)
- Add Source entries in DB for DHL-specific queries

## API Design

All API responses return **HTML partials** (HTMX pattern, consistent with existing `/api/articles`):

```
GET /api/news?carrier=&page=&per_page=
  → returns HTML partial for timeline feed section (paginated)

GET /api/news/route-changes
  → returns HTML partial for route changes grid

GET /api/news/hero
  → returns HTML partial for hero section (refreshable)

GET /api/news/carrier-columns
  → returns HTML partial for three carrier columns
```

Each section can be independently refreshed via HTMX `hx-get` with `hx-trigger`.

## Featured Article Logic

Hero section selects the featured article as:
1. The most recent article that has associated `RouteChange` records, or
2. Fallback: the most recent article overall

## Implementation Order

1. Add DHL carrier support (update filter bars, badge colors, DB sources)
2. Create `/news` blueprint and route
3. Build `templates/news.html` with four sections
4. Build partials for each section
5. Add `/api/news` endpoint
6. Wire navigation link in `base.html`
7. Add DHL fetcher sources
