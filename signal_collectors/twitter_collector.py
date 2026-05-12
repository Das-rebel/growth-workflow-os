#!/usr/bin/env python3
"""Twitter/X signal collector via Nitter instances and RSS fallback.

Scrapes Nitter for fintech/growth/India finance keywords.
Falls back to RSS-based approach if Nitter instances are down.

No API key required — uses public Nitter instances.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import re
import xml.etree.ElementTree as ET
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

# Nitter instances to try (in order of reliability)
NITTER_INSTANCES = [
    "https://nitter.privacydev.net",
    "https://nitter.poast.org",
    "https://nitter.net",
]

SEARCH_TERMS = [
    "fintech india",
    "embedded lending",
    "nbfc growth",
]


def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in FILTER_KEYWORDS)


def _fetch_via_nitter_rss(instance: str, search_term: str) -> list[dict]:
    """Try fetching via Nitter RSS for a search term."""
    results = []
    try:
        # Nitter search RSS endpoint
        url = f"{instance}/search/rss?f=tweets&q={requests.utils.quote(search_term)}"
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            return []

        root = ET.fromstring(resp.text)
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in items:
            title = item.findtext("title", "").strip()
            # Nitter titles often contain the tweet text
            description = item.findtext("description", "").strip()
            link = item.findtext("link", "").strip()
            pub_date_str = item.findtext("pubDate", "").strip()

            # Clean HTML from description
            clean_desc = re.sub(r"<[^>]+>", " ", description).strip()
            clean_title = re.sub(r"<[^>]+>", " ", title).strip()

            if not clean_title and not clean_desc:
                continue

            text = clean_title or clean_desc
            if not _is_relevant(text):
                continue

            created = None
            if pub_date_str:
                for fmt in (
                    "%a, %d %b %Y %H:%M:%S %z",
                    "%a, %d %b %Y %H:%M:%S GMT",
                    "%Y-%m-%dT%H:%M:%S%z",
                ):
                    try:
                        created = datetime.strptime(pub_date_str, fmt)
                        break
                    except ValueError:
                        continue

            # Convert nitter link back to twitter
            tweet_url = link.replace(instance, "https://twitter.com")
            # Also handle nitter.net → x.com mapping
            tweet_url = re.sub(r"https?://nitter[^/]*", "https://twitter.com", tweet_url)

            results.append({
                "title": clean_title[:200],
                "text": clean_desc[:300] if clean_desc else clean_title[:300],
                "url": tweet_url,
                "source": "twitter",
                "created": (created or datetime.now(timezone.utc)).isoformat(),
            })

    except (requests.RequestException, ET.ParseError, Exception):
        pass

    return results


def collect_twitter() -> list[dict]:
    """Collect relevant tweets via Nitter RSS instances.

    Returns list of dicts with keys: title, text, url, source, created.
    """
    print("🐦 Collecting from Twitter/X (via Nitter)...")

    all_results = []
    working_instance = None

    for instance in NITTER_INSTANCES:
        # Quick health check
        try:
            resp = requests.get(instance, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                working_instance = instance
                break
        except requests.RequestException:
            continue

    if not working_instance:
        print("  ⚠ Twitter: all Nitter instances are down — skipping")
        return []

    print(f"  Using Nitter instance: {working_instance}")

    seen_texts = set()
    for term in SEARCH_TERMS:
        tweets = _fetch_via_nitter_rss(working_instance, term)
        count = 0
        for t in tweets:
            key = t["text"][:80].lower()
            if key not in seen_texts:
                seen_texts.add(key)
                all_results.append(t)
                count += 1
        print(f"  '{term}': {count} relevant tweets")

    print(f"  Twitter/X: {len(all_results)} total relevant tweets")
    return all_results[:20]


if __name__ == "__main__":
    tweets = collect_twitter()
    for t in tweets:
        print(f"  {t['title'][:80]}")
