"""Strategic inference engine — interprets market signals and generates strategic implications."""

import json
from inference_engines.base import InferenceEngine
from signal_collectors.base import Signal
from config import load_sources


STRATEGIC_INFERENCE_PROMPT = """You are a systems-oriented growth operator analyzing market signals.

Input: A market signal from "{source}" in category "{category}"
Signal: {text}

Your task is to produce a structured interpretation. Do NOT summarize the signal. Analyze it strategically.

Return a JSON object with these fields:
{{
  "strategic_interpretation": "2-3 sentences on what this means for AI-native organizations. Be specific and opinionated.",
  "organizational_impact": "What organizational structures or processes does this affect?",
  "signal_tags": ["tag1", "tag2", "tag3"],  // 3-5 relevant tags
  "strategic_weight": 0.85,  // 0.0-1.0, how important is this signal
  "implied_theses": ["thesis statement 1", "thesis statement 2"],  // 1-2 implied strategic theses this reinforces or challenges
  "time_horizon": "immediate|6months|1year|2years+",  // When does this become operationally relevant
  "gtm_implications": "How does this affect GTM motion, positioning, or sales cycles?"
}}

Be opinionated. Generic analysis is worthless.
"""


class StrategicInferenceEngine(InferenceEngine):
    """Generate strategic interpretations of market signals."""

    def __init__(self):
        super().__init__("strategic_inference")
        self.sources_config = load_sources()
        self.categories = self.sources_config.get("categories", {})

    def run(self, signal: Signal) -> dict:
        """Generate strategic inference for a single signal.

        Args:
            signal: The Signal to analyze

        Returns:
            Dict with interpretation results
        """
        # Determine strategic weight from config
        default_weight = 0.5
        if signal.category in self.categories:
            default_weight = self.categories[signal.category].get("weight", default_weight)

        system_prompt = """You are a systems-oriented growth operator. Your analysis should feel like it came from someone who has built and scaled growth organizations, not a generic AI. Connect dots others miss. Be specific, not academic."""

        prompt = STRATEGIC_INFERENCE_PROMPT.format(
            source=signal.source,
            category=signal.category,
            text=signal.text,
        )

        try:
            response_text = self.infer(prompt, system_prompt=system_prompt, json_output=True)
            result = json.loads(response_text)

            # Ensure weight is set
            if not result.get("strategic_weight"):
                result["strategic_weight"] = default_weight

            return result

        except json.JSONDecodeError:
            return {
                "strategic_interpretation": response_text,
                "organizational_impact": "Analysis pending",
                "signal_tags": [signal.category],
                "strategic_weight": default_weight,
                "implied_theses": [],
                "time_horizon": "6months",
                "gtm_implications": "TBD",
            }
        except Exception as e:
            raise RuntimeError(f"Strategic inference failed: {e}")

    def run_batch(self, signals: list[Signal]) -> list[dict]:
        """Run inference on a batch of signals.

        Args:
            signals: List of Signals to analyze

        Returns:
            List of inference results
        """
        results = []
        for signal in signals:
            try:
                result = self.run(signal)
                result["signal_id"] = signal.id if hasattr(signal, "id") else None
                results.append(result)
            except Exception as e:
                print(f"  ⚠ Failed to infer on signal {signal.id}: {e}")
                results.append({
                    "signal_id": signal.id if hasattr(signal, "id") else None,
                    "error": str(e),
                    "strategic_weight": 0.0,
                })
        return results