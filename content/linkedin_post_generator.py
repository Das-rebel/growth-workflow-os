#!/usr/bin/env python3
"""LinkedIn post generator — contrarian long-form for Subho's brand.

Brand voice: Contrarian + cross-domain connector + operator metrics.
Target: Passive recruiting — "fintech growth operator who has done it at scale"
Posts: 1-2x/week, long-form (300-500 words), specific numbers, India context.
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
from signals.vault_interest_extractor import get_vault_context_for_topic, search_vault
from content.content_drafts_store import save_draft

# MiniMax via OpenCode proxy
OPENCODE_API_KEY = os.getenv("OPENCODE_GO_API_KEY", "")
OPENCODE_BASE = "https://opencode.ai/zen/go/v1/chat/completions"
MODEL = "minimax-m2.7"

BRAND_VOICE = """You are writing for Subhajit Das — ex-Groww (scaled lending $5M→$36M), ex-NIRO ($8M/mo), ex-Axis Bank/ICICI, IIM Tiruchirappalli + IISER Pune. Target audience: growth operators, fintech founders, product people in India.

HARD CONSTRAINTS:
- Contrarian first: open with a claim that challenges conventional fintech growth wisdom
- Numbers mandatory: cite real metrics, timelines, company names
- India context: reference UPI, RBI, NPCI, local dynamics when relevant
- Cross-domain connector: find patterns from other fields (military, airlines, healthcare → fintech)
- One thesis per post: state it in line 1-2
- End with a specific challenge/question to readers — not generic
- No: "Thoughts?", "Let me know in comments", "Thanks for reading"
- Max 2 hashtags: #growth and/or #fintech and/or #India
- Emoji: only 🎯📈⚡❌✅ used sparingly"""

LINKEDIN_POST_PROMPT = """Write a LinkedIn post in Subho's voice.

VOICE CONSTRAINTS (hard):
- Contrarian first: open with a claim that challenges conventional fintech growth wisdom
- Numbers mandatory: cite real metrics, timelines, company names
- India context: reference UPI, RBI, NPCI, local dynamics when relevant
- Cross-domain connector: find patterns from other fields
- One thesis per post: state it in line 1-2
- End with a specific challenge/question to readers — not generic
- No: "Thoughts?", "Let me know in comments", "Thanks for reading"
- Max 2 hashtags: #growth and/or #fintech and/or #India

TOPIC: {topic}

VAULT CONTEXT:
{vault_context}

OUTPUT: ONLY the post content, 300-500 words. No meta-commentary.

Write it now."""


def _call_minimax(system: str, user: str, max_tokens: int = 900, temperature: float = 0.8) -> str:
    """Call MiniMax via OpenCode proxy."""
    if not OPENCODE_API_KEY:
        raise RuntimeError("OPENCODE_GO_API_KEY not set")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        OPENCODE_BASE,
        data=data,
        headers={
            "Authorization": f"Bearer {OPENCODE_API_KEY}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"].strip()


def generate_linkedin_post(topic: str = None) -> dict:
    """One-shot LinkedIn post generator using MiniMax."""
    print(f"\n📝 Generating LinkedIn post for topic: {topic or 'fintech_growth'}")

    if not topic:
        from signals.vault_interest_extractor import extract_topics
        topics_data = extract_topics()
        topic = topics_data.get("top_topic", "fintech_growth")

    vault_ctx = get_vault_context_for_topic(topic, limit=5) if topic else []
    ctx_text = "\n".join([
        f"- {r.get('name', r.get('title', ''))[:120]}"
        for r in vault_ctx
        if r.get('name') or r.get('title')
    ]) or "No vault context available."

    prompt = LINKEDIN_POST_PROMPT.format(topic=topic, vault_context=ctx_text)

    try:
        post_text = _call_minimax(BRAND_VOICE, prompt, max_tokens=900)

        draft_id = save_draft(
            platform="linkedin",
            draft_text=post_text,
            topic=topic,
            signal_sources=[],
            vault_context={"topic": topic, "ctx_count": len(vault_ctx)}
        )
        return {
            "draft_id": draft_id,
            "post_text": post_text,
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


if __name__ == "__main__":
    print("\n=== LinkedIn Post Generator ===")
    result = generate_linkedin_post("fintech_growth")
    if result.get("error"):
        print(f"Error: {result['error']}")
    else:
        print(f"Draft ID: {result['draft_id']}")
        print(f"Topic: {result['topic']}")
        print(f"Status: {result['status']}")
        print(f"\n{'='*60}")
        print("POST CONTENT:")
        print(f"{'='*60}")
        print(result["post_text"])
