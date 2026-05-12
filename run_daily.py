#!/usr/bin/env python3
"""Daily signal collection — no inference, no memo generation.

Collects from: RSS, arXiv, Reddit, HN, ProductHunt, Google Trends, Twitter, LinkedIn.
Stores signals to SQLite via strategic_memory/store.py.

Usage:
    python3 run_daily.py              # Full collection run
    python3 run_daily.py --dry-run    # Test without writing to DB

Exit codes: 0 = success, 1 = partial failure, 2 = total failure
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

# Fixed path for crontab compatibility
sys.path.insert(0, str(Path(__file__).parent.resolve()))

from signal_collectors.base import Signal
from signal_collectors.rss_collector import RSSCollector
from signal_collectors.arxiv_collector import ArxivCollector
from signal_collectors.reddit_collector import collect_reddit
from signal_collectors.google_trends_collector import collect_google_trends
from signal_collectors.hackernews_collector import collect_hackernews
from signal_collectors.producthunt_collector import collect_producthunt
from signal_collectors.competitor_collector import collect_competitor
from signal_collectors.twitter_collector import collect_twitter
from signal_collectors.linkedin_collector import collect_linkedin
from strategic_memory.store import SignalStore
from config import load_settings


def collect_all() -> tuple[list[Signal], dict[str, int], list[str]]:
    """Run every collector. Returns (signals, per_source_counts, errors)."""
    now = datetime.now(timezone.utc)
    signals: list[Signal] = []
    counts: Counter = Counter()
    errors: list[str] = []

    collectors = [
        ("RSS", lambda: RSSCollector().collect(max_age_hours=24)),
        ("arXiv", lambda: ArxivCollector().collect(max_age_days=7)),
        ("Reddit", lambda: _wrap_reddit()),
        ("HackerNews", lambda: _wrap_hn()),
        ("ProductHunt", lambda: _wrap_ph()),
        ("Google Trends", lambda: _wrap_trends()),
        ("Competitor", lambda: _wrap_competitor()),
        ("Twitter", lambda: _wrap_twitter()),
        ("LinkedIn", lambda: _wrap_linkedin()),
    ]

    for name, collector_fn in collectors:
        try:
            raw = collector_fn()
            for r in raw:
                r.collected_at = r.collected_at or now
            signals.extend(raw)
            counts[name] = len(raw)
            print(f"  [{name}] {len(raw)} signals")
        except Exception as e:
            errors.append(f"{name}: {e}")
            print(f"  [{name}] SKIPPED: {e}")

    return signals, dict(counts), errors


# ── Collector wrappers that return list[Signal] ─────────────────────────

def _wrap_reddit() -> list[Signal]:
    posts = collect_reddit()
    return [
        Signal(
            text=f"[Reddit r/{p['subreddit']}] {p['title']}. {p['text'][:300]}",
            source=f"reddit:{p['subreddit']}",
            category="community_signal",
            url=p["url"],
            metadata={"score": p["score"], "subreddit": p["subreddit"]},
        )
        for p in posts
    ]


def _wrap_hn() -> list[Signal]:
    posts = collect_hackernews()
    return [
        Signal(
            text=f"[HN] {p['title']}. {p['text'][:300]}",
            source="hackernews",
            category="tech_community",
            url=p["url"],
            metadata={"score": p["score"], "num_comments": p.get("num_comments", 0)},
        )
        for p in posts
    ]


def _wrap_ph() -> list[Signal]:
    posts = collect_producthunt()
    return [
        Signal(
            text=f"[ProductHunt] {p['title']}. {p['text'][:300]}",
            source="producthunt",
            category="product_launch",
            url=p["url"],
            metadata={"score": p.get("score", 0)},
        )
        for p in posts
    ]


def _wrap_trends() -> list[Signal]:
    trends = collect_google_trends()
    return [
        Signal(
            text=f"[Google Trends] {t['title']}. {t['text'][:300]}",
            source="google_trends",
            category="trending_topic",
            url=t["url"],
            metadata={"trend_source": "google_trends_in"},
        )
        for t in trends
    ]


def _wrap_twitter() -> list[Signal]:
    tweets = collect_twitter()
    return [
        Signal(
            text=f"[Twitter] {t['title']}. {t['text'][:300]}",
            source="twitter",
            category="social_signal",
            url=t["url"],
            metadata={},
        )
        for t in tweets
    ]


def _wrap_linkedin() -> list[Signal]:
    posts = collect_linkedin()
    return [
        Signal(
            text=f"[LinkedIn] {p['title']}. {p['text'][:300]}",
            source="linkedin",
            category="social_signal",
            url=p["url"],
            metadata={"experimental": True},
        )
        for p in posts
    ]



def _wrap_competitor() -> list[Signal]:
    raw_signals = collect_competitor()
    return [
        Signal(
            text=f"[Competitor/{s.metadata.get('company','HN') if s.metadata else 'HN'}] {s.text[:300]}",
            source="competitor",
            category="competitor_signal",
            url=s.url,
            metadata=s.metadata or {},
        )
        for s in raw_signals
    ]


# ── Deduplication ────────────────────────────────────────────────────────

def dedup(signals: list[Signal], max_signals: int) -> list[Signal]:
    """Deduplicate by first-100-chars and cap count."""
    seen: set[str] = set()
    out: list[Signal] = []
    for s in signals:
        key = s.text[:100].lower()
        if key not in seen:
            seen.add(key)
            out.append(s)
    return out[:max_signals]


# ── Main ─────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Growth OS — daily signal collection")
    parser.add_argument("--dry-run", action="store_true", help="Collect but do NOT write to DB")
    args = parser.parse_args()

    print("=" * 60)
    print("GROWTH OS — DAILY SIGNAL COLLECTION")
    print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    if args.dry_run:
        print("Mode: DRY-RUN (no writes)")
    print("=" * 60)

    # 1. Collect
    print("\nCollecting signals...")
    signals, counts, errors = collect_all()

    total_raw = len(signals)
    settings = load_settings()
    max_signals = settings.get("pipeline", {}).get("max_signals_per_run", 50)
    signals = dedup(signals, max_signals)

    print(f"\nDedup: {total_raw} raw -> {len(signals)} unique (cap={max_signals})")

    if not signals:
        print("\nNo signals collected.")
        return 2 if errors else 0

    # 2. Store (unless dry-run)
    if not args.dry_run:
        store = SignalStore()
        stored = 0
        for s in signals:
            try:
                sid = store.add_signal(s)
                s.id = sid
                stored += 1
            except Exception as e:
                print(f"  Store failed for signal: {e}")
        print(f"\nStored {stored}/{len(signals)} signals to DB")
    else:
        print(f"\n[DRY-RUN] Would store {len(signals)} signals")

    # 3. Summary
    print("\n" + "-" * 40)
    print("COLLECTION SUMMARY")
    print("-" * 40)
    for source, count in sorted(counts.items()):
        print(f"  {source:20s} {count:>4} signals")
    print(f"  {'TOTAL':20s} {len(signals):>4} signals")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")

    print(f"\nFinished: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    # Exit code
    if not errors:
        return 0
    elif len(signals) > 0:
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
