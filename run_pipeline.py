#!/usr/bin/env python3
"""Full pipeline: collect → interpret → infer → memorize → generate memo.

Usage:
    python run_pipeline.py              # Full run with all steps
    python run_pipeline.py --skip-rss  # Skip RSS collection, use stored signals
    python run_pipeline.py --memo-only # Skip collection/inference, regenerate memo
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import argparse

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.progress import Progress, Spinner, TaskID

from signal_collectors.rss_collector import RSSCollector
from signal_collectors.arxiv_collector import ArxivCollector
from signal_collectors.reddit_collector import collect_reddit
from signal_collectors.google_trends_collector import collect_google_trends
from signal_collectors.hackernews_collector import collect_hackernews
from signal_collectors.producthunt_collector import collect_producthunt
from signal_collectors.twitter_collector import collect_twitter
from signal_collectors.linkedin_collector import collect_linkedin
from signal_collectors.competitor_collector import collect_competitor
from signal_collectors.manual import submit as manual_signal
from signal_collectors.base import Signal
from inference_engines.strategic import StrategicInferenceEngine
from strategic_memory.store import SignalStore, ThesisStore, PredictionStore
from operating_memos.generator import WeeklyMemoEngine
from config import get_memo_output_dir, load_settings

console = Console()


def step1_collect(args) -> list[Signal]:
    """Step 1: Collect signals from all sources."""
    console.print("\n[bold blue]STEP 1: Signal Collection[/bold blue]")

    settings = load_settings()
    max_signals = settings.get("pipeline", {}).get("max_signals_per_run", 50)

    signals = []

    if not args.skip_rss:
        console.print("📡 Collecting from RSS feeds...")
        rss = RSSCollector()
        rss_signals = rss.collect(max_age_hours=72)  # Last 72 hours
        console.print(f"   Collected {len(rss_signals)} signals from RSS")
        signals.extend(rss_signals)

        console.print("📚 Collecting from arXiv...")
        arxiv = ArxivCollector()
        arxiv_signals = arxiv.collect(max_age_days=30)
        console.print(f"   Collected {len(arxiv_signals)} signals from arXiv")
        signals.extend(arxiv_signals)

        console.print("📱 Collecting from Reddit...")
        try:
            reddit_posts = collect_reddit()
            for post in reddit_posts:
                signals.append(Signal(
                    text=f"[Reddit r/{post['subreddit']}] {post['title']}. {post['text'][:300]}",
                    source=f"reddit:{post['subreddit']}",
                    category="community_signal",
                    url=post["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={"score": post["score"], "subreddit": post["subreddit"]},
                ))
            console.print(f"   Collected {len(reddit_posts)} signals from Reddit")
        except Exception as e:
            console.print(f"   ⚠ Reddit collection skipped: {e}")

        # --- New collectors: Google Trends, HN, ProductHunt, Twitter, LinkedIn ---

        console.print("📈 Collecting from Google Trends...")
        try:
            trends = collect_google_trends()
            for t in trends:
                signals.append(Signal(
                    text=f"[Google Trends] {t['title']}. {t['text'][:300]}",
                    source="google_trends",
                    category="trending_topic",
                    url=t["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={"trend_source": "google_trends_in"},
                ))
            console.print(f"   Collected {len(trends)} signals from Google Trends")
        except Exception as e:
            console.print(f"   ⚠ Google Trends collection skipped: {e}")

        console.print("🔶 Collecting from Hacker News...")
        try:
            hn_posts = collect_hackernews()
            for post in hn_posts:
                signals.append(Signal(
                    text=f"[HN] {post['title']}. {post['text'][:300]}",
                    source="hackernews",
                    category="tech_community",
                    url=post["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={"score": post["score"], "num_comments": post.get("num_comments", 0)},
                ))
            console.print(f"   Collected {len(hn_posts)} signals from Hacker News")
        except Exception as e:
            console.print(f"   ⚠ Hacker News collection skipped: {e}")

        console.print("🚀 Collecting from Product Hunt...")
        try:
            ph_posts = collect_producthunt()
            for post in ph_posts:
                signals.append(Signal(
                    text=f"[ProductHunt] {post['title']}. {post['text'][:300]}",
                    source="producthunt",
                    category="product_launch",
                    url=post["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={"score": post.get("score", 0)},
                ))
            console.print(f"   Collected {len(ph_posts)} signals from Product Hunt")
        except Exception as e:
            console.print(f"   ⚠ Product Hunt collection skipped: {e}")

        console.print("🐦 Collecting from Twitter/X...")
        try:
            tweets = collect_twitter()
            for t in tweets:
                signals.append(Signal(
                    text=f"[Twitter] {t['title']}. {t['text'][:300]}",
                    source="twitter",
                    category="social_signal",
                    url=t["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={},
                ))
            console.print(f"   Collected {len(tweets)} signals from Twitter/X")
        except Exception as e:
            console.print(f"   ⚠ Twitter/X collection skipped: {e}")

        console.print("💼 Collecting from LinkedIn (experimental)...")
        try:
            li_posts = collect_linkedin()
            for post in li_posts:
                signals.append(Signal(
                    text=f"[LinkedIn] {post['title']}. {post['text'][:300]}",
                    source="linkedin",
                    category="social_signal",
                    url=post["url"],
                    collected_at=datetime.now(timezone.utc),
                    metadata={"experimental": True},
                ))
            console.print(f"   Collected {len(li_posts)} signals from LinkedIn")
        except Exception as e:
            console.print(f"   ⚠ LinkedIn collection skipped: {e}")

        # Competitor monitoring
        console.print("🔭 Collecting competitor signals...")
        try:
            comp_signals = collect_competitor()
            signals.extend(comp_signals)
            console.print(f"   Collected {len(comp_signals)} competitor signals")
        except Exception as e:
            console.print(f"   ⚠ Competitor collection skipped: {e}")
    else:
        console.print("⏭️  Skipping RSS collection")

    # Deduplicate by text similarity (simple check)
    seen = set()
    deduped = []
    for s in signals:
        key = s.text[:100].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(s)

    # Cap at max
    if len(deduped) > max_signals:
        console.print(f"   Capping at {max_signals} signals")
        deduped = deduped[:max_signals]

    console.print(f"   Total unique signals: {len(deduped)}")
    return deduped


def step2_store(signals: list[Signal]) -> list[Signal]:
    """Step 2: Store signals in memory, assign IDs."""
    console.print("\n[bold blue]STEP 2: Signal Storage[/bold blue]")

    store = SignalStore()
    stored_signals = []

    for s in signals:
        signal_id = store.add_signal(s)
        s.id = signal_id
        stored_signals.append(s)

    console.print(f"   Stored {len(stored_signals)} signals")
    return stored_signals


def step3_infer(signals: list[Signal]) -> list[dict]:
    """Step 3: Run strategic inference on all signals."""
    console.print("\n[bold blue]STEP 3: Strategic Inference[/bold blue]")

    engine = StrategicInferenceEngine()
    unprocessed = [s for s in signals if not s.interpretation]

    if not unprocessed:
        console.print("   All signals already processed")
        return []

    console.print(f"   Inferring on {len(unprocessed)} signals...")

    results = []
    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Processing signals...", total=len(unprocessed))
        for signal in unprocessed:
            try:
                result = engine.run(signal)
                # Update signal with interpretation
                store = SignalStore()
                if result.get("strategic_weight"):
                    store.update_interpretation(
                        signal.id,
                        result.get("strategic_interpretation", ""),
                        result.get("strategic_weight", 0.5),
                        result.get("signal_tags", []),
                    )
                signal.interpretation = result.get("strategic_interpretation")
                signal.strategic_weight = result.get("strategic_weight", 0.5)
                signal.tags = result.get("signal_tags", [])
                results.append(result)
            except Exception as e:
                console.print(f"   ⚠ Signal {signal.id} failed: {e}")
            progress.update(task, advance=1)

    console.print(f"   ✓ Inferred on {len(results)} signals")
    return results


def step4_memo(args):
    """Step 4: Generate weekly operating memo."""
    if args.memo_only:
        console.print("\n[bold blue]STEP 4: Memo Generation (memo-only mode)[/bold blue]")
    else:
        console.print("\n[bold blue]STEP 4: Weekly Memo Generation[/bold blue]")

    thesis_store = ThesisStore()
    prediction_store = PredictionStore()
    signal_store = SignalStore()

    theses = thesis_store.get_active()
    predictions = {
        "pending": prediction_store.get_pending(),
        "resolved": prediction_store.get_resolved(limit=10),
    }
    signals = signal_store.get_recent(limit=100)

    console.print(f"   Memory: {len(signals)} signals, {len(theses)} theses, {len(predictions['pending'])} pending predictions")

    engine = WeeklyMemoEngine()
    output_dir = get_memo_output_dir()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = output_dir / f"weekly_memo_{date_str}.md"

    try:
        result_path = engine.run(signals, theses, predictions, output_path)
        console.print(f"   ✓ Memo generated: {result_path}")
        return result_path
    except Exception as e:
        console.print(f"   ✗ Memo generation failed: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="AI-Native Growth Operating System Pipeline")
    parser.add_argument("--skip-rss", action="store_true", help="Skip RSS collection")
    parser.add_argument("--memo-only", action="store_true", help="Skip collection/inference, only regenerate memo")
    args = parser.parse_args()

    console.print("\n" + "=" * 60)
    console.print("AI-NATIVE GROWTH OPERATING SYSTEM")
    console.print("=" * 60)
    console.print(f"Started: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")

    try:
        if args.memo_only:
            # Memo only mode - just regenerate
            memo_path = step4_memo(args)
        else:
            # Full pipeline
            signals = step1_collect(args)
            if not signals:
                console.print("\n⚠  No signals collected. Exiting.")
                return

            signals = step2_store(signals)
            results = step3_infer(signals)
            memo_path = step4_memo(args)

        console.print("\n" + "=" * 60)
        console.print("[bold green]PIPELINE COMPLETE[/bold green]")
        console.print("=" * 60)

        if memo_path:
            console.print(f"\n📄 Weekly Memo: {memo_path}")
            console.print(f"\nPreview:\n")
            content = Path(memo_path).read_text()
            console.print(content[:1500])
            console.print("\n... [truncated]")

    except Exception as e:
        console.print(f"\n[bold red]Pipeline failed: {e}[/bold red]")
        raise


if __name__ == "__main__":
    main()