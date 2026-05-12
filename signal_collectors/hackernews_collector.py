#!/usr/bin/env python3
"""Hacker News signal collector via Algolia API.

Searches HN for fintech, growth, lending, embedded finance topics.
No API key required — uses the public Algolia search API.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime, timezone

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
    "fintech",
    "growth lending",
    "embedded finance",
    "neobank",
    "payment infrastructure",
]

ALGOLIA_BASE = "https://hn.algolia.com/api/v1/search"


def _is_relevant(title: str, story_text: str = "") -> bool:
    text = (title + " " + (story_text or "")).lower()
    return any(kw in text for kw in FILTER_KEYWORDS)


def collect_hackernews() -> list[dict]:
    """Collect relevant stories from Hacker News via Algolia API.

    Returns list of dicts with keys: title, text, url, score, source, created.
    """
    print("🔶 Collecting from Hacker News...")

    seen_ids = set()
    results = []

    for query in SEARCH_QUERIES:
        try:
            params = {
                "query": query,
                "tags": "story",
                "hitsPerPage": 30,
                "numericFilters": "points>5",
            }
            resp = requests.get(ALGOLIA_BASE, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            hits = data.get("hits", [])
            count = 0

            for hit in hits:
                object_id = hit.get("objectID", "")
                if object_id in seen_ids:
                    continue
                seen_ids.add(object_id)

                title = hit.get("title", "") or ""
                story_text = hit.get("story_text") or hit.get("comment_text") or ""
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
                points = hit.get("points") or 0
                num_comments = hit.get("num_comments") or 0

                created_at_str = hit.get("created_at", "")
                created = None
                if created_at_str:
                    try:
                        created = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass

                if _is_relevant(title, story_text):
                    text = story_text[:300] if story_text else title
                    results.append({
                        "title": title,
                        "text": text,
                        "url": url,
                        "score": points,
                        "num_comments": num_comments,
                        "source": "hackernews",
                        "created": (created or datetime.now(timezone.utc)).isoformat(),
                    })
                    count += 1

            print(f"  HN '{query}': {count} relevant")

        except requests.RequestException as e:
            print(f"  ⚠ HN '{query}': request failed — {e}")

    # Deduplicate by title, sort by score
    seen_titles = set()
    deduped = []
    for r in results:
        key = r["title"][:80].lower()
        if key not in seen_titles:
            seen_titles.add(key)
            deduped.append(r)

    deduped.sort(key=lambda x: x["score"], reverse=True)
    print(f"  Hacker News: {len(deduped)} total relevant stories")
    return deduped[:25]


if __name__ == "__main__":
    posts = collect_hackernews()
    for p in posts:
        print(f"  [{p['score']} pts] {p['title'][:80]}")
