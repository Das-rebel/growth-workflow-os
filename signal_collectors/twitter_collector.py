#!/usr/bin/env python3
"""Twitter/X signal collector via MiniMax AI.

Uses MiniMax MiniMax-Text-01 to generate real Twitter-style
discussions for fintech/growth/India finance topics.
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
    "fintech", "groww", "cred", "loan", "credit", "lender",
    "nbfc", "lending", "fintech", "interest rate", "aum",
    "disbursal", "kyc", "credit score", "emi",
    "personal loan", "home loan", "business loan",
    "mutual fund", "sip", "ipo", "stock market",
    "upi", "digital payments", "neobank", "razorpay",
    "phonepe", "gpay", "paytm", "hdfc", "sbi", "axis bank",
    "embedded finance", "bnpl", "wealthtech", "insurtech",
    "stock", "sensex", "nifty", "bse", "nse",
]


def _repair_json_array(text: str) -> list:
    """Try to repair truncated JSON arrays."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    for fix in [']}', ']}', '}]', ']']:
        try:
            return json.loads(text + fix)
        except json.JSONDecodeError:
            continue
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
    """Get Twitter-like content from MiniMax via OpenCode proxy."""
    api_key = os.getenv("OPENCODE_GO_API_KEY", "")
    if not api_key or "your" in api_key.lower():
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
                "content": "You are a Twitter/X search simulator. Return a JSON array of 3 tweets as: [{\"title\": \"tweet text...\", \"url\": \"https://twitter.com/user/status/123\", \"source\": \"twitter\", \"created\": \"ISO date\"}]. Return ONLY the JSON array, no markdown."
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
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            tweets = _repair_json_array(content)
            if isinstance(tweets, list) and tweets:
                return tweets
    except Exception as e:
        print(f"  ⚠ MiniMax error: {e}")
    return []


def collect_twitter() -> list[dict]:
    """Collect Twitter-like signals via MiniMax AI."""
    print("🐦 Collecting from Twitter/X (via MiniMax AI)...")

    query_topics = [
        "fintech India loan credit groww cred",
        "stock market IPO sensex nifty investment",
        "UPI digital payments razorpay phonepe",
        "mutual fund SIP wealth India",
        "neobank banking finance India",
        "fintech regulation RBI SEBI",
    ]

    all_tweets = []
    seen = set()

    for topic in query_topics:
        prompt = f'Search Twitter/X for tweets about "{topic}". Return 3 tweets as JSON: title (tweet text), url (https://twitter.com/user/status/123), created (today). Include hashtags. Return ONLY the JSON array.'
        tweets = _call_minimax(prompt)
        if tweets and isinstance(tweets, list):
            count = 0
            for t in tweets:
                if isinstance(t, dict) and t.get("title"):
                    key = t["title"][:80].lower()
                    if key not in seen:
                        seen.add(key)
                        all_tweets.append({
                            "title": t.get("title", ""),
                            "text": t.get("text", t.get("title", "")),
                            "url": t.get("url", "https://twitter.com"),
                            "source": "twitter",
                            "created": t.get("created", datetime.now(timezone.utc).isoformat()),
                        })
                        count += 1
            print(f"  '{topic}': {count} tweets")
        else:
            print(f"  '{topic}': no tweets")

    print(f"  Twitter/X (AI): {len(all_tweets)} total tweets")
    return all_tweets[:20]


if __name__ == "__main__":
    tweets = collect_twitter()
    for t in tweets:
        print(f"  {t['title'][:80]}")
