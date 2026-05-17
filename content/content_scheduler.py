#!/usr/bin/env python3
"""Content generation scheduler — generates 3-4 posts/week automatically.

Runs from run_daily.py or can be triggered manually.
Coordinates: signal collection → topic selection → content generation → draft store.

Ghost writer constraints:
- LinkedIn: 1-2x per week (Tue/Thu preferred)
- Twitter: 2x per week (Mon/Wed/Sat preferred)
- Max 4 posts per week total
- Failure recovery: retry once on LLM error, mark failed drafts
- Topic deduplication: skip if draft exists on same topic+platform today
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from dotenv import load_dotenv
load_dotenv(Path("config") / ".env")

from datetime import datetime, timezone, timedelta
from content.linkedin_post_generator import generate_linkedin_post
from content.twitter_thread_generator import generate_twitter_thread
from content.content_drafts_store import (
    get_drafts_by_status, get_content_stats,
    save_draft, init_drafts_table
)
from signals.vault_interest_extractor import extract_topics

# Cadence constraints
LINKEDIN_PER_WEEK = 2
TWITTER_PER_WEEK = 2
MAX_POSTS_PER_WEEK = 4

# Preferred posting days (0=Monday, 2=Tuesday, 4=Thursday, 5=Friday, 6=Saturday)
PREFERRED_DAYS = {0, 2, 4, 5, 6}


def get_weekday() -> int:
    """0=Monday ... 6=Sunday (UTC)."""
    return datetime.now(timezone.utc).weekday()


def is_preferred_posting_day() -> bool:
    """Only generate on preferred days to spread content across week."""
    return get_weekday() in PREFERRED_DAYS


def should_generate_today() -> bool:
    """Should we generate content today?
    
    Rules:
    - Only on preferred posting days (Mon/Tue/Thu/Fri/Sat)
    - If not a preferred day, skip regardless of quota
    """
    stats = get_content_stats(days=7)
    total = stats.get("total_generated", 0)

    weekday = get_weekday()
    is_preferred = weekday in PREFERRED_DAYS

    print(f"📊 Content stats (7 days): {stats}")
    print(f"  Today is weekday {weekday} {'(preferred)' if is_preferred else '(skip)'}")

    if not is_preferred:
        print("  ⏭ Not a preferred posting day — skipping generation")
        return False

    if total >= MAX_POSTS_PER_WEEK:
        print(f"  ⏭ Weekly quota met ({total}/{MAX_POSTS_PER_WEEK}) — skipping")
        return False

    return True


def get_topic_for_today(exclude_topics: list[str] = None) -> str:
    """Pick the best topic based on vault recency signals, avoiding repeats."""
    topics_data = extract_topics()
    recency = topics_data.get("recency_signals", {})
    exclude_topics = exclude_topics or []

    # Sort by recency signal (highest first)
    ranked = sorted(recency.items(), key=lambda x: x[1], reverse=True)
    print(f"🧠 Vault recency signals: {recency}")

    # Pick highest recency topic not in exclude list
    for topic, score in ranked:
        if topic not in exclude_topics:
            print(f"  Selected topic: {topic} (score: {score})")
            return topic

    return "fintech_growth"  # fallback


def generate_with_retry(generator_fn, topic: str, platform: str, max_retries: int = 2) -> dict:
    """Generate content with one retry on failure.
    
    Returns dict with draft_id (int) or error (str), and status.
    """
    exclude_errors = (Exception,)
    
    for attempt in range(max_retries):
        try:
            result = generator_fn(topic)
            if result.get("error"):
                # LLM call succeeded but returned error
                if attempt < max_retries - 1:
                    print(f"  ⚠ Attempt {attempt+1} failed with: {result['error']} — retrying...")
                    continue
                return {"status": "failed", "error": result["error"], "topic": topic, "platform": platform}

            if result.get("draft_id"):
                print(f"  ✅ Draft saved: ID {result['draft_id']}")
                return result

            # Unknown response
            if attempt < max_retries - 1:
                print(f"  ⚠ Unexpected response: {result} — retrying...")
                continue

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                print(f"  ⚠ Attempt {attempt+1} exception: {error_msg} — retrying...")
                continue
            return {"status": "failed", "error": error_msg, "topic": topic, "platform": platform}

    return {"status": "failed", "error": "Max retries exceeded", "topic": topic, "platform": platform}


def save_draft_safe(platform: str, draft_text: str, topic: str,
                   signal_sources: list = None, vault_context: dict = None,
                   error: str = None) -> dict:
    """Save draft with error tracking, handling UNIQUE constraint failures."""
    try:
        draft_id = save_draft(
            platform=platform,
            draft_text=draft_text,
            topic=topic,
            signal_sources=signal_sources or [],
            vault_context=vault_context or {},
        )
        return {"draft_id": draft_id, "status": "saved"}
    except Exception as e:
        err_str = str(e)
        # UNIQUE constraint failure = already have draft for this topic+platform today
        if "UNIQUE" in err_str or "duplicate" in err_str.lower():
            print(f"  ⏭ Skipping duplicate: {platform}/{topic} already generated today")
            return {"status": "skipped", "reason": "duplicate", "topic": topic, "platform": platform}
        # Other error — save with failed status
        print(f"  ⚠ Draft save error: {err_str}")
        return {"status": "error", "error": err_str}


def generate_content_batch() -> dict:
    """Generate LinkedIn + Twitter posts for this week."""
    print("\n" + "="*60)
    print("📝 GHOST WRITER — Content Generation")
    print("="*60)

    if not should_generate_today():
        weekday = get_weekday()
        is_preferred = weekday in PREFERRED_DAYS
        stats = get_content_stats(days=7)
        total = stats.get("total_generated", 0)
        if not is_preferred:
            return {"status": "skipped", "reason": f"weekday {weekday} not preferred"}
        return {"status": "skipped", "reason": "quota_met"}

    # Check what's already generated this week
    stats = get_content_stats(days=7)
    linkedin_done = stats.get("platform_breakdown", {}).get("linkedin", 0)
    twitter_done = stats.get("platform_breakdown", {}).get("twitter", 0)
    used_topics = []  # track topics used this run to avoid repeats

    print(f"📊 This week: {linkedin_done} LinkedIn, {twitter_done} Twitter")

    results = []
    all_draft_ids = []

    # Generate LinkedIn if under quota
    if linkedin_done < LINKEDIN_PER_WEEK:
        topic = get_topic_for_today(exclude_topics=used_topics)
        print(f"\n📝 Generating LinkedIn post for: {topic}")
        result = generate_with_retry(generate_linkedin_post, topic, "linkedin")
        
        if result.get("draft_id"):
            used_topics.append(topic)
            all_draft_ids.append(result["draft_id"])
            # Save error draft if generation had error but returned partial
            if result.get("error"):
                from content.content_drafts_store import update_draft_status
                update_draft_status(result["draft_id"], "failed", result["error"])
        elif result.get("status") == "failed":
            # Save a failure record so quota doesn't artificially reset
            save_draft_safe("linkedin", f"FAILED: {result.get('error', 'unknown')}", topic, error=result.get("error"))
        
        results.append(result)

    # Generate Twitter thread if under quota
    if twitter_done < TWITTER_PER_WEEK:
        topic = get_topic_for_today(exclude_topics=used_topics)
        print(f"\n🐦 Generating Twitter thread for: {topic}")
        result = generate_with_retry(generate_twitter_thread, topic, "twitter")
        
        if result.get("draft_id"):
            used_topics.append(topic)
            all_draft_ids.append(result["draft_id"])
            if result.get("error"):
                from content.content_drafts_store import update_draft_status
                update_draft_status(result["draft_id"], "failed", result["error"])
        elif result.get("status") == "failed":
            save_draft_safe("twitter", f"FAILED: {result.get('error', 'unknown')}", topic, error=result.get("error"))
        
        results.append(result)

    return {
        "status": "generated",
        "results": results,
        "draft_ids": all_draft_ids,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def send_drafts_to_telegram() -> dict:
    """Notify via Telegram that drafts are ready (via OmniClaw bot @Dasomni_bot).
    
    Since TELEGRAM_BOT_TOKEN is in OmniClaw's .env, we just print what to send.
    The actual Telegram send is handled by OmniClaw server.js when user types /drafts.
    """
    from content.content_drafts_store import get_drafts_by_status, init_drafts_table
    init_drafts_table()
    
    pending = get_drafts_by_status("draft", limit=5)
    if not pending:
        print("  No pending drafts")
        return {"status": "no_pending", "drafts": []}

    print(f"  📱 {len(pending)} drafts ready for review. Message @Dasomni_bot: /drafts")
    print("  📋 Draft IDs: " + ", ".join(str(d['id']) for d in pending))
    
    return {"status": "notified", "drafts": [d['id'] for d in pending]}


def run_content_pipeline():
    """Full ghost writer pipeline: generate + send to Telegram."""
    init_drafts_table()
    results = []

    # Generate content
    gen_result = generate_content_batch()
    results.append(gen_result)

    # Send to Telegram for review
    if gen_result.get("status") == "generated":
        tg_result = send_drafts_to_telegram()
        results.append(tg_result)

    return results


if __name__ == "__main__":
    print("\n🚀 Ghost Writer Content Pipeline")
    results = run_content_pipeline()
    print(f"\n✅ Pipeline complete: {results}")