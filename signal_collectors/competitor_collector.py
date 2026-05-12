#!/usr/bin/env python3
"""Competitor monitoring signal collector.

Tracks specific companies/products across multiple free sources:
1. Hacker News Algolia API — search by company name
2. Google Trends RSS — check if any tracked company is trending
3. RSS feeds (TechCrunch AI, SaaStr) — filter for company mentions

Returns signals with category "competitor_signal" and metadata.company.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import Optional

from signal_collectors.base import Signal

# ── Company watchlist ──────────────────────────────────────────────

COMPANIES = {
    # Indian fintech
    "groww": {"name": "Groww", "sector": "indian_fintech"},
    "cred": {"name": "Cred", "sector": "indian_fintech"},
    "phonepe": {"name": "PhonePe", "sector": "indian_fintech"},
    "paytm": {"name": "Paytm", "sector": "indian_fintech"},
    "razorpay": {"name": "Razorpay", "sector": "indian_fintech"},
    "zerodha": {"name": "Zerodha", "sector": "indian_fintech"},
    "smallcase": {"name": "Smallcase", "sector": "indian_fintech"},
    "niro": {"name": "NIRO", "sector": "indian_fintech"},
    "jupiter": {"name": "Jupiter", "sector": "indian_fintech"},
    "fi money": {"name": "Fi Money", "sector": "indian_fintech"},
    "fimoney": {"name": "Fi Money", "sector": "indian_fintech"},

    # Global fintech
    "stripe": {"name": "Stripe", "sector": "global_fintech"},
    "plaid": {"name": "Plaid", "sector": "global_fintech"},
    "affirm": {"name": "Affirm", "sector": "global_fintech"},
    "klarna": {"name": "Klarna", "sector": "global_fintech"},
    "afterpay": {"name": "Afterpay", "sector": "global_fintech"},

    # AI tooling
    "openai": {"name": "OpenAI", "sector": "ai_tooling"},
    "anthropic": {"name": "Anthropic", "sector": "ai_tooling"},
    "google ai": {"name": "Google AI", "sector": "ai_tooling"},
    "gemini": {"name": "Google AI", "sector": "ai_tooling"},
}

# Aliases: map lowercase aliases to canonical keys
_ALIASES = {
    "gpay": "phonepe",
    "google pay": "phonepe",  # not exactly but common conflations in payments
    "one97": "paytm",
    "rain": "zerodha",
    "streak": "zerodha",
    "pi money": "fimoney",
}

# RSS feeds to scan for competitor mentions
RSS_FEEDS = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "SaaStr", "url": "https://saastr.com/feed/"},
    {"name": "TechCrunch Fintech", "url": "https://techcrunch.com/category/fintech/feed/"},
]

ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"
TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo=IN"


def _match_company(text: str) -> list[str]:
    """Find which companies are mentioned in text. Returns canonical keys."""
    lower = text.lower()
    matches = set()

    for key in COMPANIES:
        if key in lower:
            matches.add(key)

    for alias, canonical in _ALIASES.items():
        if alias in lower:
            matches.add(canonical)

    return list(matches)


def _collect_hackernews() -> list[Signal]:
    """Search HN for each company name."""
    signals = []
    seen_ids = set()

    for key, info in COMPANIES.items():
        try:
            params = {
                "query": info["name"],
                "tags": "story",
                "hitsPerPage": 10,
                "numericFilters": "points>3",
            }
            resp = requests.get(ALGOLIA_BASE, params=params, timeout=12)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])

            for hit in hits:
                oid = hit.get("objectID", "")
                if oid in seen_ids:
                    continue
                seen_ids.add(oid)

                title = hit.get("title", "") or ""
                story_text = hit.get("story_text") or ""
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
                points = hit.get("points") or 0

                created = None
                created_str = hit.get("created_at", "")
                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass

                # Verify the company is actually mentioned (not just partial match)
                matched = _match_company(title + " " + story_text)
                if key not in matched:
                    continue

                signals.append(Signal(
                    text=f"[HN/{info['name']}] {title}" + (f". {story_text[:200]}" if story_text else ""),
                    source="hackernews:competitor",
                    category="competitor_signal",
                    url=url,
                    collected_at=datetime.now(timezone.utc),
                    metadata={
                        "company": info["name"],
                        "sector": info["sector"],
                        "hn_points": points,
                        "search_key": key,
                    },
                ))

        except requests.RequestException as e:
            print(f"  competitor_collector HN '{info['name']}': {e}")

    return signals


def _collect_google_trends() -> list[Signal]:
    """Check Google Trends for tracked companies trending in India."""
    signals = []

    try:
        resp = requests.get(
            TRENDS_RSS_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml",
            },
            timeout=15,
        )
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in items:
            title = item.findtext("title", "").strip()
            description = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()

            text = title + " " + description
            matched = _match_company(text)

            for company_key in matched:
                info = COMPANIES[company_key]
                signals.append(Signal(
                    text=f"[Trending/{info['name']}] {title}. {description[:200]}",
                    source="google_trends:competitor",
                    category="competitor_signal",
                    url=link,
                    collected_at=datetime.now(timezone.utc),
                    metadata={
                        "company": info["name"],
                        "sector": info["sector"],
                        "search_key": company_key,
                    },
                ))

    except (requests.RequestException, ET.ParseError) as e:
        print(f"  competitor_collector Google Trends: {e}")

    return signals


def _collect_rss() -> list[Signal]:
    """Scan configured RSS feeds for competitor mentions."""
    signals = []
    cutoff = datetime.utcnow() - timedelta(hours=72)

    for feed_config in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_config["url"])

            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    published = datetime(*entry.updated_parsed[:6])

                if published and published < cutoff:
                    continue

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                text = title + " " + summary

                matched = _match_company(text)

                for company_key in matched:
                    info = COMPANIES[company_key]
                    signals.append(Signal(
                        text=f"[{feed_config['name']}/{info['name']}] {title}",
                        source=f"rss:{feed_config['name']}:competitor",
                        category="competitor_signal",
                        url=entry.get("link"),
                        collected_at=datetime.now(timezone.utc),
                        metadata={
                            "company": info["name"],
                            "sector": info["sector"],
                            "feed_name": feed_config["name"],
                            "search_key": company_key,
                        },
                    ))

        except Exception as e:
            print(f"  competitor_collector RSS '{feed_config['name']}': {e}")

    return signals


def collect_competitor() -> list[Signal]:
    """Collect competitor signals from all sources.

    Returns list of Signal objects with category='competitor_signal'
    and metadata containing 'company' and 'sector'.
    """
    print("🔭 Collecting competitor signals...")

    signals = []

    # 1. Hacker News
    hn_signals = _collect_hackernews()
    signals.extend(hn_signals)
    print(f"  competitor_collector HN: {len(hn_signals)} signals")

    # 2. Google Trends
    trends_signals = _collect_google_trends()
    signals.extend(trends_signals)
    print(f"  competitor_collector Google Trends: {len(trends_signals)} signals")

    # 3. RSS feeds
    rss_signals = _collect_rss()
    signals.extend(rss_signals)
    print(f"  competitor_collector RSS: {len(rss_signals)} signals")

    # Deduplicate by (company, url)
    seen = set()
    deduped = []
    for s in signals:
        key = (s.metadata.get("company", ""), s.url or s.text[:80])
        if key not in seen:
            seen.add(key)
            deduped.append(s)

    print(f"  competitor_collector total: {len(deduped)} unique signals")
    return deduped


if __name__ == "__main__":
    signals = collect_competitor()
    for s in signals:
        company = s.metadata.get("company", "?")
        sector = s.metadata.get("sector", "?")
        print(f"  [{company}/{sector}] {s.text[:90]}")
