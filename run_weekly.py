"""Weekly operating memo generator entry point."""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from operating_memos.generator import WeeklyMemoEngine
from strategic_memory.store import ThesisStore, PredictionStore, SignalStore
from config import get_memo_output_dir


def run_weekly():
    """Generate the weekly operating memo."""
    print("\n" + "=" * 60)
    print("WEEKLY OPERATING MEMO")
    print("=" * 60)

    # Load strategic memory
    thesis_store = ThesisStore()
    prediction_store = PredictionStore()
    signal_store = SignalStore()

    theses = thesis_store.get_active()
    predictions = {
        "pending": prediction_store.get_pending(),
        "resolved": prediction_store.get_resolved(limit=10),
    }
    signals = signal_store.get_recent(limit=50)

    print(f"\n📊 Memory:")
    print(f"   Signals: {len(signals)}")
    print(f"   Active theses: {len(theses)}")
    print(f"   Pending predictions: {len(predictions['pending'])}")

    # Generate memo
    engine = WeeklyMemoEngine()
    output_dir = get_memo_output_dir()
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_path = output_dir / f"weekly_memo_{date_str}.md"

    print(f"\n⚙️  Generating memo...")
    try:
        result_path = engine.run(signals, theses, predictions, output_path)
        print(f"\n✓ Memo generated: {result_path}")
        print(f"\n{'=' * 60}")
        print("MEMO PREVIEW")
        print("=" * 60)
        print(output_path.read_text()[:2000])
        print(f"\n... [truncated, full memo at {result_path}]")
    except Exception as e:
        print(f"\n✗ Failed to generate memo: {e}")
        raise


if __name__ == "__main__":
    run_weekly()