#!/usr/bin/env python3
"""Product Hunt signal collector.

Scrapes the Product Hunt RSS feed for fintech/finance/AI/growth tool launches.
No API key required — uses the public RSS feed.
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
    "saas", "automation", "revenue", "growth", "analytics",
    "accounting", "invoice", "tax", "budget",
]

PH_RSS_URL = "https://www.producthunt.com/feed"
PH_ALTERNATE_URLS = [
    "https://www.producthunt.com/feed",
    "https://www.producthunt.com/rss",
]


def _is_relevant(title: str, description: str = "") -> bool:
    text = (title + " " + description).lower()
    return any(kw in text for kw in FILTER_KEYWORDS)


def collect_producthunt() -> list[dict]:
    """Collect product launches from Product Hunt RSS feed.

    Returns list of dicts with keys: title, text, url, score, source, created.
    """
    print("🚀 Collecting from Product Hunt...")

    for rss_url in PH_ALTERNATE_URLS:
        try:
            resp = requests.get(
                rss_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                                  "Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/rss+xml, application/xml, text/xml, text/html",
                },
                timeout=15,
                allow_redirects=True,
            )
            resp.raise_for_status()

            # Try parsing as XML
            try:
                root = ET.fromstring(resp.text)
            except ET.ParseError:
                # HTML page — try extracting from meta/og tags is too fragile
                # Fall through to next URL
                continue

            results = []

            # Handle RSS 2.0 structure
            channel = root.find("channel")
            items = channel.findall("item") if channel is not None else root.findall(".//item")

            # Handle Atom feed structure
            if not items:
                ns = "{http://www.w3.org/2005/Atom}"
                items = root.findall(f"{ns}entry")

            for item in items:
                title = item.findtext("title", "").strip()
                if not title:
                    t_el = item.find("{http://www.w3.org/2005/Atom}title")
                    title = (t_el.text or "").strip() if t_el is not None else ""

                link = item.findtext("link", "").strip()
                if not link:
                    l_el = item.find("{http://www.w3.org/2005/Atom}link")
                    link = l_el.get("href", "") if l_el is not None else ""

                description = item.findtext("description", "") or item.findtext("summary", "")
                if not description:
                    d_el = item.find("{http://www.w3.org/2005/Atom}summary")
                    description = (d_el.text or "") if d_el is not None else ""
                description = description.strip()

                # Strip HTML tags from description
                import re
                description = re.sub(r"<[^>]+>", " ", description).strip()

                pub_date_str = (
                    item.findtext("pubDate", "")
                    or item.findtext("published", "")
                    or item.findtext("updated", "")
                )
                if not pub_date_str:
                    pd_el = item.find("{http://www.w3.org/2005/Atom}published")
                    pub_date_str = (pd_el.text or "") if pd_el is not None else ""

                created = None
                if pub_date_str:
                    for fmt in (
                        "%a, %d %b %Y %H:%M:%S %z",
                        "%a, %d %b %Y %H:%M:%S GMT",
                        "%Y-%m-%dT%H:%M:%S%z",
                        "%Y-%m-%dT%H:%M:%SZ",
                    ):
                        try:
                            created = datetime.strptime(pub_date_str.strip(), fmt)
                            break
                        except ValueError:
                            continue

                # Extract upvotes from description if present
                score = 0
                import re
                vote_match = re.search(r"(\d+)\s*upvote", description.lower())
                if vote_match:
                    score = int(vote_match.group(1))

                if _is_relevant(title, description):
                    text = description[:300] if description else title
                    results.append({
                        "title": title,
                        "text": text,
                        "url": link,
                        "score": score,
                        "source": "producthunt",
                        "created": (created or datetime.now(timezone.utc)).isoformat(),
                    })

            print(f"  Product Hunt: {len(results)} relevant launches from {rss_url}")
            return results

        except requests.RequestException as e:
            print(f"  ⚠ Product Hunt ({rss_url}): request failed — {e}")
            continue
        except ET.ParseError:
            continue

    print("  ⚠ Product Hunt: all RSS URLs failed")
    return []


if __name__ == "__main__":
    posts = collect_producthunt()
    for p in posts:
        print(f"  {p['title'][:80]} — {p['url'][:60]}")
