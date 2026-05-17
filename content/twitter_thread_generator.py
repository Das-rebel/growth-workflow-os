#!/usr/bin/env python3
"""Twitter/X thread generator — 5-tweet contrarian threads for Subho's brand."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
load_dotenv(Path("config") / ".env")

import litellm
from datetime import datetime, timezone
from signals.vault_interest_extractor import get_vault_context_for_topic, search_vault
from content.content_drafts_store import save_draft

BRAND_VOICE = """You are writing for Subhajit Das — ex-Groww (scaled lending $5M→$36M), ex-NIRO ($8M/mo), ex-Axis Bank/ICICI, IIM Tiruchirappalli + IISER Pune.

HARD CONSTRAINTS:
- Contrarian first: open with a claim that challenges conventional fintech growth wisdom
- Numbers mandatory: cite real metrics, timelines, company names
- India context: reference UPI, RBI, NPCI, local dynamics when relevant
- Cross-domain connector: find patterns from other fields
- No MBA jargon — banned terms: "flywheel", "north star", "synergy", "circle back"
- Each tweet is standalone — must make sense without the thread context
- Thread: exactly 5 tweets, numbered 1/5 to 5/5
- Tweet 1: hook (contrarian claim) + thread premise
- Tweets 2-4: build the case with evidence, numbers, examples
- Tweet 5: specific challenge/question to reader — never generic
- Max 280 chars per tweet
- Emoji: only 🎯📈⚡❌✅ used sparingly
- No hashtags in tweets (they waste characters)"""

THREAD_PROMPT = """Write a 5-tweet thread in Subho's voice about: {topic}

FORMAT:
Tweet 1: [1/5] Hook + thread premise (contrarian claim, max 280 chars)
Tweet 2: [2/5] First evidence point with specific numbers
Tweet 3: [3/5] Second evidence point, cross-domain connection
Tweet 4: [4/5] Third evidence point, India context (UPI/RBI/NPCI)
Tweet 5: [5/5] Specific challenge to reader — not generic

Each tweet max 280 chars. No hashtags. No meta-commentary.

Write the thread now."""


def generate_twitter_thread(topic: str = None) -> dict:
    """One-shot Twitter thread generator using Groq."""
    print(f"\n🐦 Generating Twitter thread for topic: {topic or 'fintech_growth'}")

    if not topic:
        from signals.vault_interest_extractor import extract_topics
        topics_data = extract_topics()
        topic = topics_data.get("top_topic", "fintech_growth")

    vault_ctx = get_vault_context_for_topic(topic, limit=5) if topic else []
    ctx_text = "\n".join([
        f"- {r.get('name', r.get('title', ''))[:100]}"
        for r in vault_ctx
        if r.get('name') or r.get('title')
    ]) or "No vault context."

    prompt = THREAD_PROMPT.format(topic=topic, vault_context=ctx_text)

    try:
        response = litellm.completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": BRAND_VOICE},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1200,
        )
        thread_text = response["choices"][0]["message"]["content"].strip()

        # Parse tweets from thread
        tweets = _parse_tweets(thread_text)

        draft_id = save_draft(
            platform="twitter",
            draft_text=thread_text,
            topic=topic,
            signal_sources=[],
            vault_context={"topic": topic, "tweet_count": len(tweets), "ctx_count": len(vault_ctx)}
        )

        return {
            "draft_id": draft_id,
            "thread_text": thread_text,
            "tweets": tweets,
            "topic": topic,
            "status": "draft",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "topic": topic,
            "status": "failed",
        }


def _parse_tweets(thread_text: str) -> list[dict]:
    """Parse tweets from raw thread text."""
    lines = thread_text.split("\n")
    tweets = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Match [1/5], 1/, [1]/5 patterns
        import re
        match = re.match(r"\[?(\d+)/5\]?\s*(.*)", line, re.DOTALL)
        if match:
            num = int(match.group(1))
            content = match.group(2).strip()
            if content:
                tweets.append({"number": num, "content": content})
    return tweets


if __name__ == "__main__":
    print("\n=== Twitter Thread Generator ===")
    result = generate_twitter_thread("fintech_growth")
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Draft ID: {result['draft_id']}")
        print(f"Tweets: {len(result.get('tweets', []))}")
        print(f"\n{'='*60}")
        print("THREAD CONTENT:")
        print(f"{'='*60}")
        print(result["thread_text"])