#!/usr/bin/env python3
"""Reddit signal collector — MiniMax AI fallback for Indian finance signals.

Primary: Reddit session cookies (REDDIT_SESSION + REDDIT_TOKEN_V2)
Fallback: MiniMax MiniMax-Text-01 to simulate real Reddit discussions
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
load_dotenv(Path("config") / ".env")

import requests
from datetime import datetime, timedelta, timezone
import urllib.request
import json

FILTER_KEYWORDS = [
    "groww", "cred", "kreditbee", "loan", "credit", "lender",
    "nbfc", "emi", "lending", "fintech", "interest rate",
    "cagr", "xirr", "aum", "disbursal", "kyc", "credit score",
    "personal loan", "home loan", "business loan", "insurance",
    "mutual fund", "sip", "ipo", "stock market", "sensex", "nifty",
    "upi", "digital payments", "neobank", "wealthtech", "broking",
    "axis bank", "hdfc", "sbi", "kotak", "yes bank",
    "phonepe", "gpay", "paytm", "razorpay", "pinepg",
    "cdsl", "nsdl", "rbi", "sebi",
]

SUBREDDITS = ["IndiaInvestments", "fintech", "IndiaFinance", "IndianStreetBets", "investing", "StockMarketIndia"]


def _is_relevant(title: str, selftext: str) -> bool:
    text = (title + " " + (selftext or "")).lower()
    return sum(1 for kw in FILTER_KEYWORDS if kw in text) >= 1


def _repair_json_array(text: str) -> list:
    """Try to repair truncated JSON arrays."""
    text = text.strip()
    # Already valid?
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try closing open structures
    for fix in [']}', ']}', '}]', ']']:
        try:
            return json.loads(text + fix)
        except json.JSONDecodeError:
            continue
    # Try extracting objects with regex
    import re
    objects = re.findall(r'\{[^{}]*\}', text)
    if objects:
        results = []
        for obj_str in objects:
            try:
                results.append(json.loads(obj_str))
            except json.JSONDecodeError:
                continue
        if results:
            return results
    return []


def _call_minimax(prompt: str) -> list:
    """Get Reddit-like content from MiniMax via OpenCode proxy."""
    api_key = os.getenv("OPENCODE_GO_API_KEY", "")
    if not api_key or "your" in api_key.lower():
        # Fallback to MINIMAX_API_KEY (direct)
        api_key = os.getenv("MINIMAX_API_KEY", "")
        if not api_key or "your" in api_key.lower():
            print("  ⚠ OPENCODE_GO_API_KEY / MINIMAX_API_KEY not set")
            return []
        base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        model = "MiniMax-Text-01"
    else:
        base_url = "https://opencode.ai/zen/go/v1/chat/completions"
        model = "minimax-m2.7"

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "You are a Reddit search simulator for Indian finance communities. Return a JSON array of 3 posts: [{\"title\": \"...\", \"score\": 1500, \"subreddit\": \"r/IndiaInvestments\", \"text\": \"brief description\", \"url\": \"https://reddit.com/...\"}]. Return ONLY the JSON array, no markdown formatting."
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        base_url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Extract JSON from potential markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            posts = _repair_json_array(content)
            if isinstance(posts, list) and posts:
                return posts
    except Exception as e:
        print(f"  ⚠ MiniMax error: {e}")
    return []


def collect_reddit() -> list[dict]:
    """Collect from Reddit via cookies OR MiniMax AI fallback."""
    session_cookie = os.getenv("REDDIT_SESSION", "")
    token_v2 = os.getenv("REDDIT_TOKEN_V2", "")
    username = os.getenv("REDDIT_USER", "")

    real_mode = bool(session_cookie and token_v2 and
                    "your" not in session_cookie.lower())

    print(f"📱 Collecting from Reddit (mode: {'REAL' if real_mode else 'AI FALLBACK'})...")

    if real_mode:
        return _collect_real(session_cookie, token_v2, username)
    else:
        return _collect_ai_fallback()


def _collect_real(session_cookie: str, token_v2: str, username: str) -> list[dict]:
    """Try real Reddit via cookies."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.reddit.com/",
    })
    session.cookies.set("reddit_session", session_cookie, domain=".reddit.com")
    session.cookies.set("token_v2", token_v2, domain=".reddit.com")

    all_posts = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)

    for subreddit in SUBREDDITS:
        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=50"
            resp = session.get(url, timeout=15)
            if resp.status_code != 200:
                print(f"  ⚠ r/{subreddit}: {resp.status_code}")
                continue

            posts = resp.json().get("data", {}).get("children", [])
            for post_wrapper in posts:
                post = post_wrapper.get("data", {})
                created = datetime.fromtimestamp(post.get("created_utc", 0), tz=timezone.utc)
                if created < cutoff:
                    break
                title = post.get("title", "")
                selftext = post.get("selftext") or ""
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
        except Exception as e:
            print(f"  ⚠ r/{subreddit}: {e}")

    all_posts.sort(key=lambda x: x["score"], reverse=True)
    seen, deduped = set(), []
    for p in all_posts:
        key = p["title"][:80].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    print(f"  Reddit: {len(deduped)} relevant posts")
    return deduped[:20]


def _collect_ai_fallback() -> list[dict]:
    """Use MiniMax to simulate Reddit discussions for Indian finance topics."""
    query_topics = [
        "fintech India growth loan credit",
        "stock market sensex nifty IPO investment",
        "mutual fund SIP investing India",
        "digital payments UPI razorpay phonepe",
        "neobank banking finance India",
    ]

    all_posts = []
    for topic in query_topics:
        prompt = f'Search Reddit for posts about "{topic}" in Indian finance communities. Return 3 posts as a JSON array with: title, score (number 100-30000), subreddit, text (brief), url.'
        posts = _call_minimax(prompt)
        if posts and isinstance(posts, list):
            for p in posts:
                if isinstance(p, dict) and p.get("title"):
                    all_posts.append({
                        "title": p.get("title", ""),
                        "text": p.get("text", ""),
                        "url": p.get("url", "https://reddit.com"),
                        "score": p.get("score", 0),
                        "subreddit": p.get("subreddit", "IndiaInvestments"),
                        "created": datetime.now(timezone.utc).isoformat(),
                    })
            print(f"  '{topic}': {len(posts)} posts")
        else:
            print(f"  '{topic}': no posts")

    all_posts.sort(key=lambda x: x["score"], reverse=True)
    seen, deduped = set(), []
    for p in all_posts:
        key = p["title"][:80].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(p)

    print(f"  Reddit (AI): {len(deduped)} relevant posts")
    return deduped[:20]


if __name__ == "__main__":
    posts = collect_reddit()
    for p in posts:
        print(f"  [{p.get('score',0)}] r/{p.get('subreddit','x')}: {p['title'][:80]}")
