"""Smoke tests for the AI-Native Growth Operating System."""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import load_settings, load_sources, get_model_config
from strategic_memory.store import SignalStore, ThesisStore, PredictionStore


def test_config():
    print("Testing config...")
    settings = load_settings()
    assert settings, "Settings should load"
    assert "models" in settings, "Models config should exist"
    print(f"  ✓ Settings loaded, {len(settings.get('models', {}))} model configs")

    sources = load_sources()
    assert sources, "Sources should load"
    print(f"  ✓ Sources loaded, {len(sources.get('rss_feeds', []))} RSS feeds")

    model_cfg = get_model_config("strategic_inference")
    assert model_cfg.get("model"), "Model config should have model"
    print(f"  ✓ Model config: {model_cfg['model']}")


def test_strategic_memory():
    print("\nTesting strategic memory...")

    # Test SignalStore
    store = SignalStore()
    from signal_collectors.base import Signal
    from datetime import datetime

    sig = Signal(
        text="Test signal for smoke test",
        source="smoke_test",
        category="manual_observation",
    )
    sig_id = store.add_signal(sig)
    assert sig_id, "Should return signal id"
    print(f"  ✓ SignalStore: added signal {sig_id}")

    # Test get_recent
    recent = store.get_recent(limit=5)
    assert len(recent) >= 1, "Should have at least one signal"
    print(f"  ✓ SignalStore: retrieved {len(recent)} recent signals")

    # Test ThesisStore
    thesis_store = ThesisStore()
    thesis_id = thesis_store.add_thesis("AI will restructure GTM motion", confidence=0.7)
    print(f"  ✓ ThesisStore: added thesis {thesis_id}")

    # Test PredictionStore
    pred_store = PredictionStore()
    pred_id = pred_store.add_prediction("LLM agents will handle 50%+ of outbound by 2026", resolve_by="2026-12-31")
    print(f"  ✓ PredictionStore: added prediction {pred_id}")

    print("  ✓ All memory stores working")


def test_signal_model():
    print("\nTesting signal model...")
    from signal_collectors.base import Signal
    from datetime import datetime

    sig = Signal(
        text="Stripe launches AI billing agent",
        source="techcrunch",
        category="product_launch",
        url="https://techcrunch.com/stripe-ai-billing",
    )

    assert sig.text, "Signal should have text"
    assert sig.source, "Signal should have source"
    assert sig.category == "product_launch", "Category should be set"
    print(f"  ✓ Signal model valid: {sig.category}/{sig.source}")


def main():
    print("=" * 50)
    print("AI-Native Growth OS — Smoke Tests")
    print("=" * 50)

    try:
        test_config()
        test_signal_model()
        test_strategic_memory()
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()