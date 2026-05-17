#!/usr/bin/env python3
"""Content generation scheduler — generates 3-4 posts/week automatically.

Runs from run_daily.py or can be triggered manually.
Coordinates: signal collection → topic selection → content generation → draft store.
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

MAX_POSTS_PER_WEEK = 4
LINKEDIN_PER_WEEK = 2
TWITTER_PER_WEEK = 2


def should_generate_today() -> bool:
    """Decide if we should generate content today based on weekly quota."""
    stats = get_content_stats(days=7)
    total = stats.get("total_generated", 0)
    print(f"📊 Content stats (7 days): {stats}")
    return total < MAX_POSTS_PER_WEEK


def get_topic_for_today() -> str:
    """Pick the best topic based on vault recency signals."""
    topics_data = extract_topics()
    top = topics_data.get("top_topic", "fintech_growth")
    recency = topics_data.get("recency_signals", {})
    print(f"🧠 Vault recency signals: {recency}")
    return top


def generate_content_batch() -> dict:
    """Generate LinkedIn + Twitter posts for this week."""
    print("\n" + "="*60)
    print("📝 GHOST WRITER — Content Generation")
    print("="*60)

    if not should_generate_today():
        print("✅ Weekly quota met — skipping generation")
        return {"status": "skipped", "reason": "quota_met"}

    # Check what's already generated this week
    stats = get_content_stats(days=7)
    linkedin_done = stats.get("platform_breakdown", {}).get("linkedin", 0)
    twitter_done = stats.get("platform_breakdown", {}).get("twitter", 0)

    print(f"📊 This week: {linkedin_done} LinkedIn, {twitter_done} Twitter")

    results = []

    # Generate LinkedIn if under quota
    if linkedin_done < LINKEDIN_PER_WEEK:
        topic = get_topic_for_today()
        print(f"\n📝 Generating LinkedIn post for: {topic}")
        result = generate_linkedin_post(topic)
        results.append(result)
        if result.get("draft_id"):
            print(f"  ✅ Draft saved: ID {result['draft_id']}")

    # Generate Twitter thread if under quota
    if twitter_done < TWITTER_PER_WEEK:
        topic = get_topic_for_today()
        print(f"\n🐦 Generating Twitter thread for: {topic}")
        result = generate_twitter_thread(topic)
        results.append(result)
        if result.get("draft_id"):
            print(f"  ✅ Draft saved: ID {result['draft_id']}")

    return {
        "status": "generated",
        "results": results,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def send_drafts_to_telegram() -> dict:
    """Send pending drafts to Telegram for review."""
    print("\n📱 Sending pending drafts to Telegram...")

    pending = get_drafts_by_status("draft", limit=5)
    if not pending:
        print("  No pending drafts")
        return {"status": "no_pending", "drafts": []}

    sent = []
    for draft in pending:
        draft_id = draft["id"]
        platform = draft["platform"]
        topic = draft.get("topic", "general")
        content = draft.get("draft_text", "")[:500]

        msg = f"📝 *Content Draft* [{platform.upper()}]\n"
        msg += f"Topic: {topic}\n\n"
        msg += f"{content[:400]}..."
        msg += f"\n\nReply with 'approve {draft_id}' to publish or 'reject {draft_id}' to discard."

        # Send via Telegram — use OmniClaw bot
        success = _send_telegram_message(msg)
        if success:
            from content.content_drafts_store import update_draft_status
            update_draft_status(draft_id, "reviewed")
            sent.append(draft_id)

    print(f"  Sent {len(sent)} drafts to Telegram")
    return {"status": "sent", "drafts": sent}


def _send_telegram_message(text: str, chat_id: str = None) -> bool:
    """Send message via Telegram bot."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        print("  ⚠ No TELEGRAM_BOT_TOKEN")
        return False

    import urllib.request
    import json

    # Get chat_id from env or use primary
    target_chat = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")

    payload = {
        "text": text,
    }
    if target_chat:
        payload["chat_id"] = target_chat

    try:
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode().find("\"ok\":true") >= 0
    except Exception as e:
        print(f"  ⚠ Telegram send error: {e}")
        return False


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