#!/usr/bin/env python3
"""Query the strategic memory — ask questions about stored signals and theses.

Usage:
    python run_query.py "what are the major market shifts this week?"
    python run_query.py "which predictions are pending?"
    python run_query.py "what signals relate to AI agents?"
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from strategic_memory.store import SignalStore, ThesisStore, PredictionStore
from inference_engines.base import InferenceEngine
from config import get_model_config, load_env

load_env()


def summarize_signals(signals: list, max_chars: int = 3000) -> str:
    if not signals:
        return "No signals found."
    parts = []
    total = 0
    for s in signals:
        text = f"- [{s['category']}] {s['text'][:150]}"
        if total + len(text) > max_chars:
            break
        parts.append(text)
        total += len(text)
    return "\n".join(parts) + f"\n\n(total: {len(signals)} signals)"


def summarize_theses(theses: list) -> str:
    if not theses:
        return "No theses."
    return "\n".join([f"- [{t['thesis_type']}] {t['thesis_text']} (confidence: {t['confidence']})" for t in theses])


def summarize_predictions(preds: list) -> str:
    if not preds:
        return "No predictions."
    return "\n".join([f"- {p['prediction_text']} (resolve by: {p.get('resolve_by', 'TBD')})" for p in preds])


class QueryEngine(InferenceEngine):
    def __init__(self):
        super().__init__("strategic_inference")

    def run(self, input_data) -> dict:
        raise NotImplementedError("Use answer() instead")

    def answer(self, question: str, signals: list, theses: list, pending: list, resolved: list) -> str:
        """Answer a question using the stored memory as context."""
        signals_text = summarize_signals(signals)
        theses_text = summarize_theses(theses)
        pending_text = summarize_predictions(pending)
        resolved_text = summarize_predictions(resolved)

        prompt = f"""You are a strategic advisor with access to a growth operating system's memory.

Answer the user's question based ONLY on the stored data below. Be specific and opinionated. If the data doesn't support a confident answer, say so.

---
RECENT SIGNALS:
{signals_text}

ACTIVE THESES:
{theses_text}

PENDING PREDICTIONS:
{pending_text}

RECENTLY RESOLVED PREDICTIONS:
{resolved_text}
---

QUESTION: {question}

ANSWER:"""

        system_prompt = """You are a strategic operator advising on AI-native GTM and organizational design. You answer with precision, connecting dots across signals. You are opinionated, not diplomatic."""

        try:
            return self.infer(prompt, system_prompt=system_prompt)
        except Exception as e:
            return f"Query failed: {e}"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    question = " ".join(sys.argv[1:])

    # Load memory
    signal_store = SignalStore()
    thesis_store = ThesisStore()
    pred_store = PredictionStore()

    signals = signal_store.get_recent(limit=100)
    theses = thesis_store.get_active()
    pending = pred_store.get_pending()
    resolved = pred_store.get_resolved(limit=20)

    print(f"\n📊 Memory: {len(signals)} signals, {len(theses)} theses, {len(pending)} pending predictions")
    print(f"❓ Question: {question}\n")

    engine = QueryEngine()
    answer = engine.answer(question, signals, theses, pending, resolved)

    print(f"💡 Answer:\n\n{answer}\n")


if __name__ == "__main__":
    main()