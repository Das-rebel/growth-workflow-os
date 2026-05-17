#!/usr/bin/env python3
"""Vault interest extractor — pulls brand-aligned topics from Subho's vault.

Vault: 8,224 bookmarks (6,187 Twitter + 2,037 Instagram) with FAISS index.
Used to shape content topic selection and enrich content with relevant examples.
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
from inference_engines.base import InferenceEngine


VAULT_API = "https://serve-vault-search-338789220059.asia-south1.run.app"

# Topics that are brand-relevant for Subho's ghost writer
BRAND_TOPICS = {
    "fintech_growth": ["fintech", "growth", "lending", "credit", "loan", "EMI", "NBFC", "digital lending"],
    "d2c_strategy": ["D2C", "direct to consumer", "ecommerce", "ecommerce growth", "consumer brand", "d2c brand"],
    "performance_marketing": ["performance marketing", "performance marketing india", "growth marketing", "acquisition", "activation", "retention"],
    "india_finance": ["india finance", "indian fintech", "banking india", "digital banking india", "hdfc", "axis bank", "sbi"],
    "product_gtm": ["GTM", "go to market", "launch", "product market fit", "distribution", "channel strategy"],
    "data_analytics": ["data analytics", "growth metrics", "Cohort analysis", "attribution", "funnel analytics"],
}

# Recent time windows for recency signals
RECENT_DAYS = 30


def search_vault(query: str, limit: int = 5) -> list[dict]:
    """Query the vault search API."""
    try:
        url = f"{VAULT_API}/search?q={urllib.request.quote(query)}&limit={limit}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return result.get("results", [])
    except Exception as e:
        print(f"  ⚠ Vault search error for '{query}': {e}")
        return []


def extract_topics() -> dict:
    """Extract brand-aligned topics from vault with recency signals."""
    print("🧠 Extracting interests from vault...")

    topics_summary = {}
    recency_signals = {}

    for topic_key, keywords in BRAND_TOPICS.items():
        topic_results = []
        for kw in keywords:
            results = search_vault(kw, limit=3)
            topic_results.extend(results)

        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for r in topic_results:
            url = r.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(r)

        topics_summary[topic_key] = {
            "keywords": keywords,
            "results_count": len(unique_results),
            "sample": [
                {"name": r.get("name", "")[:100], "url": r.get("url", "")[:80], "type": r.get("type", "")}
                for r in unique_results[:3]
            ]
        }

        # Recency: how many in last 30 days
        recent = sum(1 for r in unique_results if _is_recent(r.get("timestamp", "")))
        recency_signals[topic_key] = recent

    # Rank topics by recency signal
    ranked = sorted(recency_signals.items(), key=lambda x: x[1], reverse=True)
    print(f"  Vault topics ranked by recent activity:")
    for topic, score in ranked:
        print(f"    {topic}: {score} recent signals")

    return {
        "topics": topics_summary,
        "recency_signals": recency_signals,
        "top_topic": ranked[0][0] if ranked else None,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
    }


def _is_recent(timestamp: str) -> bool:
    """Check if timestamp is within RECENT_DAYS."""
    if not timestamp:
        return False
    try:
        from datetime import timedelta
        ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        delta = datetime.now(timezone.utc) - ts
        return delta.days < RECENT_DAYS
    except:
        return False


def get_vault_context_for_topic(topic: str, limit: int = 5) -> list[dict]:
    """Get vault examples to enrich content generation for a topic."""
    return search_vault(topic, limit=limit)


class BrandVoiceExtractor(InferenceEngine):
    """Extract Subho's brand voice from vault — what topics he saves, how he frames them."""

    def __init__(self):
        super().__init__("brand_voice_extraction")

    def run(self) -> dict:
        """Analyze vault to build brand voice profile."""
        # Pull sample posts across brand topics
        analysis_prompt = """
Analyze Subho's saved content from his vault. He has 8,224 bookmarks across Twitter and Instagram.

His target brand: contrarian fintech growth operator in India. Cross-domain connector theorist.
Always sounds like: ex-McKinsey, IIM/ISER grad, ex-Groww/NIRO/Axis Bank operator.
Voice: specific metrics, India context, falsifiable claims, cross-domain patterns.

Look at what he saves and extract:
1. What topics does he bookmark most? (list top 5 with counts)
2. What angle does he take when framing fintech/growth topics?
3. What does he ignore / not engage with?
4. Any patterns in how he describes his own experience (Groww, NIRO, Axis)?
5. Any contrarian positions that are consistent across his saves?

Return as structured JSON with specific observations.
"""
        try:
            result = self.infer(analysis_prompt, system_prompt="You are a brand voice analyst. Return structured JSON only.")
            # Parse as simple key-value pairs
            return {"brand_profile": result, "extracted_at": datetime.now(timezone.utc).isoformat()}
        except Exception as e:
            return {"brand_profile": f"Error: {e}", "extracted_at": datetime.now(timezone.utc).isoformat()}


if __name__ == "__main__":
    print("\n=== Vault Interest Extraction ===")
    result = extract_topics()
    print(f"\nTop topic: {result['top_topic']}")

    print("\n=== Brand Voice Sample ===")
    extractor = BrandVoiceExtractor()
    profile = extractor.run()
    print(profile["brand_profile"][:500] if profile["brand_profile"] else "No profile extracted")