"""Organizational implication inference engine — surface org design changes."""

from inference_engines.base import InferenceEngine


ORG_IMPLICATION_PROMPT = """Analyze this market signal for organizational design implications.

Signal: {text}
Source: {source}

For this signal, identify:
1. What team structure becomes obsolete or threatened?
2. What new organizational capability emerges?
3. Where does coordination complexity increase or decrease?
4. What role/function gains leverage?
5. What does human-only vs AI-native execution look like here?

Return JSON:
{{
  "org_structure_impact": "How does this affect team/org structure?",
  "obsolete_patterns": ["pattern1", "pattern2"],
  "emerging_patterns": ["pattern1", "pattern2"],
  "coordination_shift": "increases|decreases|redistributes",
  "leverage_shift": "Who/what gains operational leverage",
  "hiring_implications": ["implication1", "implication2"],
  "decision_velocity_impact": "How does this affect decision speed?"
}}
"""


class OrgImplicationEngine(InferenceEngine):
    """Analyze signals for organizational design implications."""

    def __init__(self):
        super().__init__("org_implication")

    def run(self, text: str, source: str = "unknown") -> dict:
        """Generate organizational implication analysis.

        Args:
            text: Signal text
            source: Signal source

        Returns:
            Dict with org design implications
        """
        system_prompt = """You are an organizational architect who understands how AI-native organizations differ from traditional ones. You think in terms of coordination costs, span of control, decision rights, and organizational learning. You see the difference between what changes superficially vs what changes structurally."""

        prompt = ORG_IMPLICATION_PROMPT.format(text=text, source=source)

        try:
            response_text = self.infer(prompt, system_prompt=system_prompt, json_output=True)
            import json
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "org_structure_impact": "Analysis pending",
                "obsolete_patterns": [],
                "emerging_patterns": [],
                "coordination_shift": "unknown",
                "leverage_shift": "unknown",
                "hiring_implications": [],
                "decision_velocity_impact": "unknown",
            }
        except Exception as e:
            raise RuntimeError(f"Org implication inference failed: {e}")