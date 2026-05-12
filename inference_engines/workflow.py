"""Workflow redesign inference engine — identify operational bottlenecks and AI-native replacements."""

from inference_engines.base import InferenceEngine


WORKFLOW_REESIGN_PROMPT = """Analyze this operational workflow observation for AI-native redesign opportunities.

Signal: {text}
Source: {source}
Category: {category}

Identify:
1. What manual/repetitive workflow does this relate to?
2. Where is decision latency highest?
3. What coordination complexity exists?
4. What becomes automatable with AI?
5. What remains human-judgment-critical?

Return JSON:
{{
  "workflow_bottleneck": "The specific workflow this signal relates to",
  "current_pain_points": ["pain1", "pain2", "pain3"],
  "ai_native_redesign": "How this workflow would work under AI-native operations",
  "automation_score": 0.8,  // 0.0-1.0, how automatable is this workflow
  "human_judgment_remaining": ["decision1", "decision2"],  // What still needs humans
  "implementation_effort": "low|medium|high",
  "operational_leverage": "high|medium|low"  // How much leverage does fixing this create
}}
"""


class WorkflowRedesignEngine(InferenceEngine):
    """Analyze signals for workflow redesign opportunities."""

    def __init__(self):
        super().__init__("workflow_redesign")

    def run(self, text: str, source: str = "unknown", category: str = "workflow_evolution") -> dict:
        """Generate workflow redesign analysis.

        Args:
            text: Signal text
            source: Signal source
            category: Signal category

        Returns:
            Dict with workflow redesign analysis
        """
        system_prompt = """You are an operational architect who redesigns workflows for AI-native organizations. You think in terms of coordination costs, decision latency, and operational leverage. You find the 10x improvements, not incremental fixes."""

        prompt = WORKFLOW_REESIGN_PROMPT.format(
            text=text,
            source=source,
            category=category,
        )

        try:
            response_text = self.infer(prompt, system_prompt=system_prompt, json_output=True)
            import json
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {
                "workflow_bottleneck": "Analysis pending",
                "current_pain_points": [],
                "ai_native_redesign": response_text if 'response_text' in dir() else "Parse error",
                "automation_score": 0.0,
                "human_judgment_remaining": [],
                "implementation_effort": "unknown",
                "operational_leverage": "unknown",
            }
        except Exception as e:
            raise RuntimeError(f"Workflow redesign inference failed: {e}")