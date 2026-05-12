#!/usr/bin/env python3
"""Google Trends signal collector.

Fetches trending topics from Google Trends RSS feed (India geo),
filters for fintech/growth relevance.

No API key required — uses the public RSS endpoint.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
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

TRENDS_RSS_URL = "https://trends.google.com/trending/rss?geo=IN"


def _is_relevant(title: str, description: str = "") -> bool:
    text = (title + " " + description).lower()
    return any(kw in text for kw in FILTER_KEYWORDS)


def collect_google_trends() -> list[dict]:
    """Collect trending topics from Google Trends India.

    Returns list of dicts with keys: title, text, url, source, created.
    """
    print("📈 Collecting from Google Trends (India)...")

    results = []

    try:
        resp = requests.get(
            TRENDS_RSS_URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/rss+xml, application/xml, text/xml",
            },
            timeout=15,
        )
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        # RSS <item> elements
        channel = root.find("channel")
        items = channel.findall("item") if channel is not None else root.findall(".//item")

        for item in items:
            title = item.findtext("title", "").strip()
            link = item.findtext("link", "").strip()
            description = item.findtext("description", "").strip()
            pub_date_str = item.findtext("pubDate", "").strip()

            # Parse date
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

            # Also check <ht:approx_traffic> for traffic count
            traffic = ""
            ns_ht = "{https://trends.google.com/trending/rss}"
            traffic_el = item.find(f"{ns_ht}approx_traffic")
            if traffic_el is not None and traffic_el.text:
                traffic = traffic_el.text.strip()

            if _is_relevant(title, description):
                text = description or title
                if traffic:
                    text = f"[{traffic} searches] {text}"

                results.append({
                    "title": title,
                    "text": text[:500],
                    "url": link,
                    "source": "google_trends",
                    "created": (created or datetime.now(timezone.utc)).isoformat(),
                })

        print(f"  Google Trends: {len(results)} relevant trends")

    except requests.RequestException as e:
        print(f"  ⚠ Google Trends: request failed — {e}")
    except ET.ParseError as e:
        print(f"  ⚠ Google Trends: XML parse error — {e}")

    return results


if __name__ == "__main__":
    trends = collect_google_trends()
    for t in trends:
        print(f"  {t['title'][:80]} — {t['url'][:60]}")
