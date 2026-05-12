"""Workflow analyzer — takes signal or text description of a workflow, outputs bottleneck analysis, redesign proposals, and automation scores.

Integrates with:
    - BottleneckDetector for rule-based bottleneck identification
    - RedesignPatterns catalog for AI-native redesign proposals
    - StrategicInferenceEngine (if available) for deeper inference-based analysis

Usage:
    analyzer = WorkflowAnalyzer()
    result = analyzer.analyze("Our proposal process takes 5 days because legal reviews every version.")
    result = analyzer.analyze_workflow_description(text_description_of_workflow)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Optional

from workflow_architecture.bottleneck_detector import (
    BottleneckDetector,
    BottleneckSignal,
    BottleneckType,
    GTMFunction,
    OperationalLeverage,
)
from workflow_architecture.redesign_patterns import (
    PATTERNS,
    RedesignPattern,
    get_pattern,
    get_patterns_by_gtm,
    get_all_patterns,
)


@dataclass
class WorkflowAnalysis:
    """Complete workflow analysis result."""

    # Input
    input_text: str
    source: str
    category: str

    # Detected bottlenecks (from BottleneckDetector)
    detected_bottlenecks: list[BottleneckSignal] = field(default_factory=list)

    # Recommended redesign patterns
    recommended_patterns: list[str] = field(default_factory=list)
    pattern_details: list[dict] = field(default_factory=list)

    # Aggregate scores
    overall_automation_potential: float = 0.0
    aggregate_leverage: str = "medium"

    # Deep inference (from StrategicInferenceEngine if available)
    deep_inference: Optional[dict] = None

    # Action items
    priority_actions: list[dict] = field(default_factory=list)
    next_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "input_text": self.input_text,
            "source": self.source,
            "category": self.category,
            "detected_bottlenecks": [b.to_dict() for b in self.detected_bottlenecks],
            "recommended_patterns": self.recommended_patterns,
            "pattern_details": self.pattern_details,
            "overall_automation_potential": self.overall_automation_potential,
            "aggregate_leverage": self.aggregate_leverage,
            "deep_inference": self.deep_inference,
            "priority_actions": self.priority_actions,
            "next_steps": self.next_steps,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    def summary(self) -> str:
        """Human-readable summary of the analysis."""
        lines = [
            f"Workflow Analysis ({self.source})",
            f"Input: {self.input_text[:100]}...",
            f"Bottlenecks detected: {len(self.detected_bottlenecks)}",
            f"Top patterns: {', '.join(self.recommended_patterns[:3])}",
            f"Automation potential: {self.overall_automation_potential:.0%}",
            f"Priority: {self.aggregate_leverage}",
        ]
        return "\n".join(lines)


class WorkflowAnalyzer:
    """Analyze text descriptions of workflows to identify bottlenecks and recommend redesigns.

    Two-stage analysis:
    1. Rule-based: BottleneckDetector identifies bottleneck types + GTM function
    2. Pattern matching: Selected RedesignPatterns are recommended based on bottleneck profile

    Optionally integrates with StrategicInferenceEngine for deeper inference-based analysis.
    """

    def __init__(
        self,
        use_deep_inference: bool = True,
        integration_available: bool = True,
    ):
        """Initialize the workflow analyzer.

        Args:
            use_deep_inference: If True, use StrategicInferenceEngine for deep analysis
            integration_available: Set to False if inference engines not available (e.g., no API keys)
        """
        self.detector = BottleneckDetector()
        self.use_deep_inference = use_deep_inference
        self._inference_engine = None
        self._integration_available = integration_available

    def _get_inference_engine(self):
        """Lazily load StrategicInferenceEngine if available."""
        if self._inference_engine is None and self._integration_available:
            try:
                from inference_engines.strategic import StrategicInferenceEngine
                self._inference_engine = StrategicInferenceEngine()
            except Exception:
                self._integration_available = False
        return self._inference_engine

    def analyze(
        self,
        text: str,
        source: str = "manual",
        category: str = "workflow_description",
        top_n: int = 5,
    ) -> WorkflowAnalysis:
        """Analyze a workflow signal and produce a complete redesign recommendation.

        Args:
            text: Text description of the workflow or pain point
            source: Source of the signal
            category: Signal category
            top_n: Number of top bottlenecks to include

        Returns:
            WorkflowAnalysis object with complete diagnosis and recommendations
        """
        # Stage 1: Rule-based bottleneck detection
        bottlenecks = self.detector.analyze(text, source=source, category=category)
        top_bottlenecks = self.detector.prioritize(bottlenecks, top_n=top_n)

        # Aggregate automation potential (weighted by confidence)
        if top_bottlenecks:
            auto_scores = [b.automation_potential for b in top_bottlenecks]
            overall_auto = sum(auto_scores) / len(auto_scores)
        else:
            overall_auto = 0.4

        # Determine aggregate leverage
        leverage_counts = {}
        for b in top_bottlenecks:
            lv = b.operational_leverage.value
            leverage_counts[lv] = leverage_counts.get(lv, 0) + 1
        aggregate_leverage = max(leverage_counts, key=leverage_counts.get) if leverage_counts else "medium"

        # Stage 2: Map to redesign patterns
        recommended_pattern_names = self._map_bottlenecks_to_patterns(top_bottlenecks)
        pattern_details = self._build_pattern_details(recommended_pattern_names)

        # Stage 3: Deep inference (optional)
        deep_inference = None
        if self.use_deep_inference and self._get_inference_engine():
            try:
                from signal_collectors.base import Signal
                signal = Signal(text=text, source=source, category=f"workflow_{category}")
                deep_inference = self._get_inference_engine().run(signal)
            except Exception:
                deep_inference = None

        # Stage 4: Generate priority actions
        priority_actions = self._generate_priority_actions(top_bottlenecks, recommended_pattern_names)

        # Stage 5: Next steps
        next_steps = self._build_next_steps(top_bottlenecks, overall_auto, aggregate_leverage)

        return WorkflowAnalysis(
            input_text=text,
            source=source,
            category=category,
            detected_bottlenecks=top_bottlenecks,
            recommended_patterns=recommended_pattern_names,
            pattern_details=pattern_details,
            overall_automation_potential=round(overall_auto, 2),
            aggregate_leverage=aggregate_leverage,
            deep_inference=deep_inference,
            priority_actions=priority_actions,
            next_steps=next_steps,
        )

    def analyze_workflow_description(
        self,
        workflow_text: str,
        workflow_name: str = "unnamed",
    ) -> WorkflowAnalysis:
        """Convenience method: analyze a full workflow description.

        Args:
            workflow_text: Multi-sentence or paragraph description of a workflow
            workflow_name: Optional name for the workflow

        Returns:
            WorkflowAnalysis object
        """
        return self.analyze(
            text=workflow_text,
            source=f"workflow_description:{workflow_name}",
            category="workflow_description",
        )

    def _map_bottlenecks_to_patterns(
        self,
        bottlenecks: list[BottleneckSignal],
    ) -> list[str]:
        """Map detected bottlenecks to relevant redesign patterns."""
        pattern_scores = {}

        for b in bottlenecks:
            for pattern_name in b.suggested_patterns:
                if pattern_name not in pattern_scores:
                    pattern_scores[pattern_name] = 0.0
                # Weight by automation potential and leverage
                leverage_mult = {"high": 1.5, "medium": 1.0, "low": 0.5}[b.operational_leverage.value]
                pattern_scores[pattern_name] += b.automation_potential * leverage_mult

        # Sort by score and return top patterns
        sorted_patterns = sorted(pattern_scores.items(), key=lambda x: -x[1])
        return [p[0] for p in sorted_patterns[:4]]

    def _build_pattern_details(self, pattern_names: list[str]) -> list[dict]:
        """Get detailed info for recommended patterns."""
        details = []
        for name in pattern_names:
            pattern = get_pattern(name)
            if pattern:
                details.append(pattern.to_dict())
        return details

    def _generate_priority_actions(
        self,
        bottlenecks: list[BottleneckSignal],
        pattern_names: list[str],
    ) -> list[dict]:
        """Generate prioritized action items from bottlenecks."""
        actions = []
        seen_types = set()

        for b in bottlenecks:
            if b.bottleneck_type.value in seen_types:
                continue
            seen_types.add(b.bottleneck_type.value)

            action = {
                "priority": len(actions) + 1,
                "type": b.bottleneck_type.value,
                "leverage": b.operational_leverage.value,
                "automation_potential": b.automation_potential,
                "description": f"Address {b.bottleneck_type.value} in {b.gtm_function.value}",
                "suggested_pattern": b.suggested_patterns[0] if b.suggested_patterns else None,
                "estimated_fte_savings_hrs_per_week": b.estimated_fte_savings,
            }
            actions.append(action)

        # Add pattern-based actions for highest value patterns
        if pattern_names:
            top_pattern = get_pattern(pattern_names[0])
            if top_pattern:
                actions.append({
                    "priority": len(actions) + 1,
                    "type": "redesign_pattern",
                    "leverage": "high",
                    "automation_potential": top_pattern.automation_score,
                    "description": f"Implement {top_pattern.name} pattern",
                    "expected_impact": top_pattern.expected_impact,
                    "implementation_effort": top_pattern.implementation_effort,
                })

        return actions

    def _build_next_steps(
        self,
        bottlenecks: list[BottleneckSignal],
        overall_auto: float,
        aggregate_leverage: str,
    ) -> list[str]:
        """Generate actionable next steps based on analysis."""
        steps = []

        if overall_auto >= 0.7 and aggregate_leverage == "high":
            steps.append("HIGH PRIORITY: Implement autonomous_outbound or ai_cs_triage pattern (automation >70%, high leverage)")
            steps.append("Begin with proof-of-concept: select one high-value workflow for AI-native redesign")
        elif overall_auto >= 0.5:
            steps.append("MEDIUM PRIORITY: Focus on manual_handoff bottlenecks first — highest automation potential")
            steps.append("Map current process in detail before designing AI-native replacement")
        else:
            steps.append("LOW AUTOMATION POTENTIAL: Focus on decision_latency improvements that augment rather than replace human judgment")
            steps.append("Consider process redesign before AI automation — some bottlenecks are structural, not technical")

        # Add GTM-specific guidance
        if bottlenecks:
            gtm_func = bottlenecks[0].gtm_function.value
            if gtm_func == "sales":
                steps.append("Sales workflow detected — prioritize real_time_lead_scoring or automated_proposal_generation")
            elif gtm_func == "customer_success":
                steps.append("CS workflow detected — prioritize predictive_churn or outcome_based_renewal_automation")
            elif gtm_func == "marketing":
                steps.append("Marketing workflow detected — consider real_time_lead_scoring for MQL quality improvement")

        return steps


def quick_analyze(text: str) -> dict:
    """One-liner analysis for a workflow description.

    Returns dict with: bottlenecks, recommended_patterns, automation_potential, leverage
    """
    analyzer = WorkflowAnalyzer(use_deep_inference=False)
    result = analyzer.analyze(text)
    return {
        "bottleneck_count": len(result.detected_bottlenecks),
        "bottleneck_types": [b.bottleneck_type.value for b in result.detected_bottlenecks],
        "gtm_function": result.detected_bottlenecks[0].gtm_function.value if result.detected_bottlenecks else "unknown",
        "recommended_patterns": result.recommended_patterns,
        "automation_potential": result.overall_automation_potential,
        "aggregate_leverage": result.aggregate_leverage,
        "priority_actions": result.priority_actions,
        "next_steps": result.next_steps,
    }


def demo():
    """Run demo analysis on sample workflow descriptions."""
    analyzer = WorkflowAnalyzer(use_deep_inference=False)

    test_workflows = [
        "Our proposal process takes 5 days because legal reviews every version. Sales has no visibility into approval status.",
        "CS managers review every cancellation risk manually. Churn predictions come two weeks too late. High-value accounts wait in same queue as everyone else.",
        "Marketing runs ABM campaigns manually - target list updates weekly, rep contacts people without knowing if they're in a campaign. No real-time ICP scoring.",
        "Sales-ops constantly chasing reps for pipeline updates. Forecast accuracy is 50% because data is stale by Monday morning. Reps manually enter activity data.",
        "We set territories annually and barely touch them mid-year. When a rep leaves, accounts go dark for 3-4 weeks while we manually reassign.",
    ]

    print("=" * 80)
    print("WORKFLOW ANALYZER — DEMO")
    print("=" * 80)

    for i, wf in enumerate(test_workflows, 1):
        result = analyzer.analyze(wf, source="demo", category=f"workflow_{i}")
        print(f"\n--- Analysis {i} ---")
        print(f"Bottleneck types: {[b.bottleneck_type.value for b in result.detected_bottlenecks]}")
        print(f"GTM function: {result.detected_bottlenecks[0].gtm_function.value if result.detected_bottlenecks else 'unknown'}")
        print(f"Automation potential: {result.overall_automation_potential:.2f}")
        print(f"Top patterns: {result.recommended_patterns[:3]}")
        print(f"Next steps: {result.next_steps[:2]}")


if __name__ == "__main__":
    demo()