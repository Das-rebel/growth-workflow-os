#!/usr/bin/env python3
"""Competitor tracking signal collector.

Monitors: Groww, Cred, Razorpay, PhonePe, NIRO, Jupiter, Fi, Slice, CRED, Kissht
Signals: funding rounds, product launches, leadership changes, regulatory issues,
         expansion moves, partnerships, layoffs, pricing changes.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
load_dotenv(Path("config") / ".env")

import urllib.request
import json
from datetime import datetime, timezone

FILTER_KEYWORDS = [
    "funding", "raised", "Series", "valuation", "IPO", "investor",
    "launch", "product", "feature", "partnership", "acquisition",
    "layoff", "restructuring", "ceo", "founder", "appointment",
    "regulation", "RBI", "SEBI", "NPCI", "compliance",
    "expansion", "new city", "new market", "global",
    "revenue", "users", "disbursal", "AUM", "growth",
    "pricing", "fee change", "interest rate",
    "competition", "market share", "strategy",
]

COMPETITORS = {
    "groww": ["Groww", "groww app", "Groww India"],
    "cred": ["CRED", "cred app", "CRED India"],
    "razorpay": ["Razorpay", "Razorpay India"],
    "phonepe": ["PhonePe", "PhonePe India"],
    "niro": ["NIRO", "NIRO lending", "niro.in"],
    "jupiter": ["Jupiter money", "Jupiter app"],
    "fi": ["Fi Money", "fi.money"],
    "slice": ["Slice (fintech)", "slice cards"],
    "kissht": ["Kissht", "kissht fintech"],
    "lazy": ["LazyPay", "lazypay"],
}


def _google_news_search(query: str) -> list[dict]:
    """Search Google News via SerpAPI or direct RSS fallback."""
    # Try RSS-style news search via news.google.com
    try:
        url = f"https://news.google.com/rss/search?q={urllib.request.quote(query)}&hl=en-IN&gl=IN&ceid=IN:en"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            import xml.etree.ElementTree as ET
            tree = ET.parse(resp)
            root = tree.getroot()
            items = []
            for item in root.findall(".//item")[:8]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()
                desc = (item.findtext("description") or "").strip()
                if title and link:
                    items.append({"title": title, "url": link, "pub_date": pub_date, "desc": desc[:200]})
            return items
    except Exception as e:
        print(f"  ⚠ Google News error for '{query}': {e}")
    return []


def _hn_search(query: str) -> list[dict]:
    """Search Hacker News via Algolia API."""
    try:
        url = f"https://hn.algolia.com/api/v1/search?query={urllib.request.quote(query)}&tags=story&numericFilters=created_at_i>{(datetime.now(timezone.utc).timestamp() - 14*86400):.0f}&limit=5"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return [
                {"title": h.get("title",""), "url": h.get("url","https://news.ycombinator.com"), "points": h.get("points",0), "comments": h.get("num_comments",0)}
                for h in data.get("hits", []) if h.get("title")
            ]
    except Exception as e:
        print(f"  ⚠ HN error for '{query}': {e}")
    return []


def collect_competitors() -> list[dict]:
    """Collect competitor signals from Google News + HN."""
    print("🏢 Collecting competitor signals...")

    all_signals = []
    seen = set()

    for competitor, aliases in COMPETITORS.items():
        for alias in aliases:
            # Google News
            news_items = _google_news_search(alias)
            for n in news_items:
                key = n["title"][:80].lower()
                if key not in seen:
                    seen.add(key)
                    all_signals.append({
                        "title": n["title"],
                        "text": n.get("desc", ""),
                        "url": n["url"],
                        "source": f"google_news:{competitor}",
                        "competitor": competitor,
                        "category": "competitor_move",
                        "created": datetime.now(timezone.utc).isoformat(),
                    })

            # HN
            hn_items = _hn_search(alias)
            for h in hn_items:
                key = h["title"][:80].lower()
                if key not in seen:
                    seen.add(key)
                    all_signals.append({
                        "title": h["title"],
                        "text": f"HN: {h['points']} points, {h['comments']} comments",
                        "url": h["url"],
                        "source": f"hn:{competitor}",
                        "competitor": competitor,
                        "category": "competitor_move",
                        "created": datetime.now(timezone.utc).isoformat(),
                    })

    print(f"  Competitor: {len(all_signals)} signals")
    return all_signals


if __name__ == "__main__":
    signals = collect_competitors()
    for s in signals[:10]:
        print(f"  [{s['competitor']}] {s['title'][:80]}")