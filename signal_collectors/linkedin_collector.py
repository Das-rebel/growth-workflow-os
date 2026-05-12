#!/usr/bin/env python3
"""LinkedIn signal collector (EXPERIMENTAL).

Uses Google search scraping to find LinkedIn posts about India fintech,
embedded lending, and growth operator content.

WARNING: LinkedIn scraping is fragile and may break at any time.
This collector is marked experimental — do not rely on it for critical signals.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import re
from datetime import datetime, timezone
from urllib.parse import quote_plus

FILTER_KEYWORDS = [
    "groww", "cred", "kreditbee", "loan", "credit", "lender",
    "nbfc", "emi", "lending", "fintech", "interest rate",
    "cagr", "xirr", "aum", "disbursal", "kyc", "credit score",
    "personal loan", "home loan", "business loan", "insurance",
    "mutual fund", "sip", "ipo", "stock market", "sensex", "nifty",
    "upi", "payment", "bank", "finance", "trading", "invest",
    "digital", "ai", "startup", "unicorn", "valuation",
    "embedded finance", "bnpl", "buy now pay later",
    "wealth", "brokerage", "neobank", "payments",
]

SEARCH_QUERIES = [
    "site:linkedin.com/posts india fintech 2025",
    "site:linkedin.com/posts embedded lending india",
    "site:linkedin.com/posts NBFC growth strategy",
]


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in FILTER_KEYWORDS)


def _scrape_google_search(query: str) -> list[dict]:
    """Scrape Google search results for LinkedIn posts."""
    results = []

    try:
        url = f"https://www.google.com/search?q={quote_plus(query)}&num=15"
        resp = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            timeout=10,
        )

        if resp.status_code != 200:
            return results

        # Parse Google SERP HTML — extract result blocks
        # Look for <a href="/url?q=..."> patterns
        href_pattern = re.compile(r'href="/url\?q=(https?://www\.linkedin\.com/[^&"]+)&[^"]*"')
        # Also match direct LinkedIn links
        direct_pattern = re.compile(r'href="(https?://www\.linkedin\.com/posts/[^"]*)"')

        links = href_pattern.findall(resp.text)
        links.extend(direct_pattern.findall(resp.text))

        # Deduplicate
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        # Try to extract titles from surrounding text
        for link in unique_links[:15]:
            # Extract a title-like snippet from the link context
            escaped = re.escape(link)
            context_match = re.search(
                rf'(?:<h3[^>]*>|<span[^>]*>)([^<]{{10,200}})(?:</h3>|</span>)',
                resp.text,
            )

            title = ""
            if context_match:
                title = re.sub(r"<[^>]+>", "", context_match.group(1)).strip()

            if not title:
                # Fallback: use URL path as title hint
                path_match = re.search(r"linkedin\.com/posts/([^?&]+)", link)
                title = path_match.group(1).replace("-", " ").title() if path_match else link

            if _is_relevant(title):
                results.append({
                    "title": title[:200],
                    "text": title[:300],
                    "url": link,
                    "source": "linkedin",
                    "created": datetime.now(timezone.utc).isoformat(),
                })

    except requests.RequestException as e:
        print(f"  ⚠ LinkedIn Google scrape: request failed — {e}")

    return results


def collect_linkedin() -> list[dict]:
    """Collect LinkedIn posts via Google search scraping.

    NOTE: This is experimental. LinkedIn aggressively blocks scraping.
    Results may be sparse or empty.

    Returns list of dicts with keys: title, text, url, source, created.
    """
    print("💼 Collecting from LinkedIn (EXPERIMENTAL — may be sparse)...")

    all_results = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        posts = _scrape_google_search(query)
        count = 0
        for p in posts:
            if p["url"] not in seen_urls:
                seen_urls.add(p["url"])
                all_results.append(p)
                count += 1
        print(f"  '{query[:50]}...': {count} posts")

    print(f"  LinkedIn: {len(all_results)} total posts (experimental)")
    return all_results[:15]


if __name__ == "__main__":
    posts = collect_linkedin()
    for p in posts:
        print(f"  {p['title'][:80]} — {p['url'][:60]}")
