#!/usr/bin/env python3
"""Reddit signal collector using browser cookies (no PRAW/API app needed).

Scrapes r/IndiaInvestments, r/fintech, r/IndiaFinance for fintech/growth signals.
Uses requests with Reddit session cookies to access the JSON API.

Cookies: paste your reddit_session and token_v2 values from browser dev tools.
Set in config/.env as:
  REDDIT_SESSION=eyJhbGciOi...   (the reddit_session cookie value)
  REDDIT_TOKEN_V2=eyJhbGciOi...   (the token_v2 cookie value)
  REDDIT_USER=your_username       (your Reddit username)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from datetime import datetime, timedelta, timezone
from config import load_env

FILTER_KEYWORDS = [
    "groww", "cred", "kreditbee", "loan", "credit", "lender",
    "nbfc", "emi", "lending", "fintech", "interest rate",
    "cagr", "xirr", "aum", "disbursal", "kyc", "credit score",
    "personal loan", "home loan", "business loan", "insurance",
    "mutual fund", "sip", "ipo", "stock market", "sensex", "nifty",
]

SUBREDDITS = ["IndiaInvestments", "fintech", "IndiaFinance", "IndianStreetBets"]


def _is_relevant(title: str, selftext: str) -> bool:
    text = (title + " " + (selftext or "")).lower()
    return sum(1 for kw in FILTER_KEYWORDS if kw in text) >= 1


def collect_reddit() -> list[dict]:
    """Collect relevant posts from Reddit using browser session cookies.

    Requires:
      REDDIT_SESSION (reddit_session cookie value)
      REDDIT_TOKEN_V2 (token_v2 cookie value)
      REDDIT_USER (your Reddit username)

    Set in config/.env or environment.
    """
    from dotenv import load_dotenv
    from pathlib import Path
    env_path = Path(__file__).parent.parent / "config" / ".env"
    load_dotenv(env_path)

    import os

    session_cookie = os.getenv("REDDIT_SESSION", "")
    token_v2 = os.getenv("REDDIT_TOKEN_V2", "")
    username = os.getenv("REDDIT_USER", "")

    if not session_cookie or not token_v2:
        print("⚠ Reddit: REDDIT_SESSION or REDDIT_TOKEN_V2 not set in config/.env")
        print("   Get these from browser dev tools → Application → Cookies → reddit.com")
        return []

    print(f"📱 Collecting from Reddit as u/{username or 'anonymous'}...")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.reddit.com/",
    })

    # Set cookies from browser session
    session.cookies.set("reddit_session", session_cookie, domain=".reddit.com")
    session.cookies.set("token_v2", token_v2, domain=".reddit.com")

    all_posts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for subreddit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
            resp = session.get(url, timeout=15)

            if resp.status_code == 401:
                print(f"  ⚠ r/{subreddit}: 401 — cookies may be expired")
                continue
            if resp.status_code == 429:
                print(f"  ⚠ r/{subreddit}: rate limited, waiting...")
                continue
            if resp.status_code != 200:
                print(f"  ⚠ r/{subreddit}: {resp.status_code}")
                continue

            data = resp.json()
            posts = data.get("data", {}).get("children", [])

            count = 0
            for post_wrapper in posts:
                post = post_wrapper.get("data", {})
                created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)

                if created < cutoff:
                    break

                title = post.get("title", "")
                selftext = post.get("selftext") or post.get("body") or ""

                if _is_relevant(title, selftext):
                    all_posts.append({
                        "title": title,
                        "text": selftext[:300] if selftext else "",
                        "url": f"https://reddit.com{post.get('permalink')}",
                        "score": post.get("score", 0),
                        "num_comments": post.get("num_comments", 0),
                        "subreddit": subreddit,
                        "created": created.isoformat(),
                    })
                    count += 1

            print(f"  r/{subreddit}: {count} relevant (of {len(posts)} total)")

        except Exception as e:
            print(f"  ⚠ r/{subreddit}: {e}")

    # Sort by score, dedupe, cap at 20
    all_posts.sort(key=lambda x: x["score"], reverse=True)
    seen = set()
    deduped = []
    for p in all_posts:
        key = p["title"][:80].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    print(f"  Total: {len(deduped)} relevant posts (top by score)")
    return deduped[:20]


if __name__ == "__main__":
    posts = collect_reddit()
    for p in posts:
        print(f"  [{p['score']}] r/{p['subreddit']}: {p['title'][:80]}")