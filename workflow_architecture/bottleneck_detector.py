"""Bottleneck detector — analyze signals for workflow pain points.

Classifies bottlenecks by type and rates automation potential + operational leverage.
Maps findings to specific GTM functions (sales, CS, marketing, ops).

Bottleneck Types:
    - DECISION_LATENCY: Decisions stall, waiting for human review or approval
    - COORDINATION_COST: Cross-functional handoffs introduce delays and miscommunication
    - MANUAL_HANDOFFF: Human-to-human transfers of information with no automation
    - INFORMATION_ASYMMETRY: Key actors lack visibility into relevant state

Automation Potential Scale (0-1):
    0.0-0.3  → Low automatable (requires human judgment, regulatory, creative)
    0.3-0.6  → Medium (partial automation viable, humans supervise)
    0.6-0.8  → High (mostly automatable, exception handling needs humans)
    0.8-1.0  → Near-total (full automation with monitoring)

Operational Leverage:
    HIGH   → Fixing this unlocks multiple downstream improvements
    MEDIUM → Direct improvement to one workflow
    LOW    → Marginal improvement, other bottlenecks dominate
"""

from __future__ import annotations

import re
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class BottleneckType(Enum):
    DECISION_LATENCY = "decision_latency"
    COORDINATION_COST = "coordination_cost"
    MANUAL_HANDOFFF = "manual_handoff"
    INFORMATION_ASYMMETRY = "information_asymmetry"


class GTMFunction(Enum):
    SALES = "sales"
    CUSTOMER_SUCCESS = "customer_success"
    MARKETING = "marketing"
    OPERATIONS = "operations"
    PRODUCT = "product"
    FINANCE = "finance"


class AutomationPotential(Enum):
    LOW = "low"       # 0.0-0.3
    MEDIUM = "medium" # 0.3-0.7
    HIGH = "high"     # 0.7-1.0


class OperationalLeverage(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class BottleneckSignal:
    """A detected bottleneck from analysis of an input signal."""

    # Identity
    bottleneck_id: str
    detected_from_text: str

    # Classification
    bottleneck_type: BottleneckType
    gtm_function: GTMFunction

    # Scoring
    automation_potential: float  # 0.0-1.0
    operational_leverage: OperationalLeverage

    # Analysis
    pain_points: list[str] = field(default_factory=list)
    affected_stages: list[str] = field(default_factory=list)
    current_waste_cycle_time: Optional[int] = None  # hours
    frequency_signal: str = "sporadic"  # sporadic | recurring | chronic

    # Recommendations
    suggested_patterns: list[str] = field(default_factory=list)
    estimated_fte_savings: Optional[float] = None

    @property
    def automation_band(self) -> AutomationPotential:
        if self.automation_potential >= 0.7:
            return AutomationPotential.HIGH
        elif self.automation_potential >= 0.3:
            return AutomationPotential.MEDIUM
        return AutomationPotential.LOW

    def to_dict(self) -> dict:
        return {
            "bottleneck_id": self.bottleneck_id,
            "detected_from_text": self.detected_from_text,
            "bottleneck_type": self.bottleneck_type.value,
            "gtm_function": self.gtm_function.value,
            "automation_potential": self.automation_potential,
            "automation_band": self.automation_band.value,
            "operational_leverage": self.operational_leverage.value,
            "pain_points": self.pain_points,
            "affected_stages": self.affected_stages,
            "current_waste_cycle_time_hours": self.current_waste_cycle_time,
            "frequency_signal": self.frequency_signal,
            "suggested_patterns": self.suggested_patterns,
            "estimated_fte_savings": self.estimated_fte_savings,
        }


class BottleneckDetector:
    """Analyze text signals to identify operational bottlenecks.

    Uses pattern matching + heuristics to classify workflow pain points.
    For deeper analysis, delegates to WorkflowRedesignEngine via inference.
    """

    # Regex patterns for signal classification
    PATTERNS = {
        BottleneckType.DECISION_LATENCY: [
            (re.compile(r"\b(waiting|wait|stall|pending|blocked|held up)\b.*\b(approval|decision|sign.?off|review)\b", re.I), 0.85),
            (re.compile(r"\b(bottleneck|logjam|traffic jam)\b.*\b(manager|director|vp|lead)\b", re.I), 0.75),
            (re.compile(r"\bapproval chain\b", re.I), 0.80),
            (re.compile(r"\bneeds sign.?off\b", re.I), 0.75),
            (re.compile(r"\bgoes through\b.*\b(committee|panel|leadership)\b", re.I), 0.70),
            (re.compile(r"\bdecision velocity\b", re.I), 0.90),
            (re.compile(r"\bslow.*escalation\b", re.I), 0.65),
            (re.compile(r"\bhuman in the loop\b", re.I), 0.60),
            (re.compile(r"\bmanual approval\b", re.I), 0.70),
        ],
        BottleneckType.COORDINATION_COST: [
            (re.compile(r"\b(hand.?off|handoff)\b.*\b(team|dept|sales|ops|eng)\b", re.I), 0.80),
            (re.compile(r"\b silos?\b", re.I), 0.75),
            (re.compile(r"\bcross.?functional\b", re.I), 0.60),
            (re.compile(r"\b(reps|agents|manager)s? chasing\b", re.I), 0.70),
            (re.compile(r"\bno clear owner\b", re.I), 0.85),
            (re.compile(r"\bblame game\b", re.I), 0.60),
            (re.compile(r"\bstatus update\b.*\bmissed\b", re.I), 0.65),
            (re.compile(r"\bescalation.*loop\b", re.I), 0.75),
            (re.compile(r"\bping.?pong\b.*\b(team|dept)\b", re.I), 0.70),
        ],
        BottleneckType.MANUAL_HANDOFFF: [
            (re.compile(r"\b(manual|human).*input\b", re.I), 0.80),
            (re.compile(r"\brekey|re.?enter|re.?type\b", re.I), 0.90),
            (re.compile(r"\bcopy.?paste\b.*\b(data|info|crm)\b", re.I), 0.85),
            (re.compile(r"\bexport\b.*\bimport\b", re.I), 0.75),
            (re.compile(r"\bspreadsheet\b.*\b(manually|hand)\b", re.I), 0.80),
            (re.compile(r"\bnotifies? (team|rep|manager)\b", re.I), 0.50),
            (re.compile(r"\bmanual follow.?up\b", re.I), 0.80),
            (re.compile(r"\brep updates\b.*\b(misc|notes)\b", re.I), 0.70),
            (re.compile(r"\bdata entry\b", re.I), 0.90),
            (re.compile(r"\bscreenshots?\b.*\b(slack|email)\b", re.I), 0.75),
        ],
        BottleneckType.INFORMATION_ASYMMETRY: [
            (re.compile(r"\b(no visibility|blind|lack.*visibility|can.?t see)\b", re.I), 0.90),
            (re.compile(r"\b(guessing|guess|unsure).*next\b", re.I), 0.70),
            (re.compile(r"\bout of the loop\b", re.I), 0.80),
            (re.compile(r"\bnot informed\b", re.I), 0.75),
            (re.compile(r"\bdecisions? made\b.*\bwithout\b", re.I), 0.85),
            (re.compile(r"\bgarbage in\b", re.I), 0.60),
            (re.compile(r"\bdata.*(stale|old|incomplete)\b", re.I), 0.70),
            (re.compile(r"\bsingle source of truth\b.*\bmissing\b", re.I), 0.80),
        ],
    }

    # GTM function detection patterns
    GTM_PATTERNS = {
        GTMFunction.SALES: [
            r"\b(lead|prospect|opportunity|deal|quota|rep|account.exec|sales)\b",
            r"\b(forecast|pipeline|closing|territory|account)\b",
        ],
        GTMFunction.CUSTOMER_SUCCESS: [
            r"\b(churn|renewal|expansion|upsell|cs.manager|customer.success|onboard|adoption)\b",
            r"\b(nps|csat|health.score|block|at.?risk)\b",
        ],
        GTMFunction.MARKETING: [
            r"\b(mql|sql|content|campaign|demand.gen|abm|brand|awareness|funnel)\b",
            r"\b(cac|ltv|attribution|channel|roi)\b",
        ],
        GTMFunction.OPERATIONS: [
            r"\b(process|workflow|efficiency|ops|team.*admin|billing)\b",
            r"\b(support|ticket|escalation|response.time)\b",
        ],
        GTMFunction.PRODUCT: [
            r"\b(feature|roadmap|bug|feedback|user.research|usability)\b",
        ],
        GTMFunction.FINANCE: [
            r"\b(revenue| ARR| MRR| contract|payment|invoice|pricing)\b",
        ],
    }

    # Pain point keywords for detailed extraction
    PAIN_PATTERNS = [
        (re.compile(r"\b(delays?|slow|takes too long|multiplied|backlog)\b", re.I), "delays_and_backlogs"),
        (re.compile(r"\b(errors?|mistakes?|miskates?|inaccurac(y|ies))\b", re.I), "errors_and_inaccuracy"),
        (re.compile(r"\b(rework|redo|repetition|redundant)\b", re.I), "rework_and_duplication"),
        (re.compile(r"\b(missed|forgot|overlooked|dropped)\b", re.I), "missed_commitments"),
        (re.compile(r"\b(inconsistent|variation|unpredictable)\b", re.I), "inconsistency"),
        (re.compile(r"\b(busy|workload|overload|burnout|overwhelmed|swamped)\b", re.I), "team_overload"),
        (re.compile(r"\b(expensive|costly|resources?|budget)\b", re.I), "cost_overrun"),
        (re.compile(r"\b(frustrat|annoy|infuri|exasper)\b", re.I), "frustration_and_turnover_risk"),
    ]

    def __init__(self):
        self._cache: dict[str, list[BottleneckSignal]] = {}

    def analyze(
        self,
        text: str,
        source: str = "unknown",
        category: str = "workflow_signal",
    ) -> list[BottleneckSignal]:
        """Analyze a text signal to identify workflow bottlenecks.

        Args:
            text: The signal text to analyze
            source: Source of the signal (e.g., "rep_interview", "metrics_review")
            category: Signal category for context

        Returns:
            List of detected BottleneckSignals, ordered by confidence
        """
        text_normalized = text.strip()

        # Check cache
        cache_key = f"{source}:{category}:{text_normalized[:100]}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        bottlenecks = []

        # Step 1: Classify bottleneck type(s)
        type_scores = {}
        for btype, patterns in self.PATTERNS.items():
            score = 0.0
            matched = False
            for pattern, weight in patterns:
                if pattern.search(text_normalized):
                    score = max(score, weight)
                    matched = True
            if matched:
                type_scores[btype] = score

        # Step 2: Identify GTM function
        gtm_function = self._detect_gtm_function(text_normalized)

        # Step 3: Extract pain points
        pain_points = self._extract_pain_points(text_normalized)

        # Step 4: Detect frequency signal
        frequency = self._detect_frequency(text_normalized)

        # Step 5: Estimate automation potential
        automation_potential = self._estimate_automation_potential(type_scores, text_normalized)

        # Step 6: Determine operational leverage
        operational_leverage = self._estimate_leverage(type_scores, gtm_function, automation_potential)

        # Step 7: Detect affected stages
        affected_stages = self._detect_affected_stages(text_normalized)

        # Step 8: Map to suggested redesign patterns
        suggested_patterns = self._map_to_patterns(type_scores, gtm_function, automation_potential)

        # Build bottleneck signals
        bottleneck_id = self._generate_id(text_normalized)

        for btype, confidence in sorted(type_scores.items(), key=lambda x: -x[1]):
            signal = BottleneckSignal(
                bottleneck_id=f"{bottleneck_id}_{btype.value}",
                detected_from_text=text_normalized[:200],
                bottleneck_type=btype,
                gtm_function=gtm_function,
                automation_potential=round(automation_potential * confidence, 2),
                operational_leverage=operational_leverage,
                pain_points=pain_points,
                affected_stages=affected_stages,
                frequency_signal=frequency,
                suggested_patterns=suggested_patterns,
                estimated_fte_savings=self._estimate_fte_savings(btype, gtm_function),
            )
            bottlenecks.append(signal)

        # If no pattern matched, create a low-confidence catch-all
        if not bottlenecks:
            signal = BottleneckSignal(
                bottleneck_id=f"{bottleneck_id}_general",
                detected_from_text=text_normalized[:200],
                bottleneck_type=BottleneckType.MANUAL_HANDOFFF,  # default assumption
                gtm_function=gtm_function,
                automation_potential=0.4,
                operational_leverage=OperationalLeverage.MEDIUM,
                pain_points=["General workflow friction"],
                frequency_signal="sporadic",
                suggested_patterns=[],
            )
            bottlenecks.append(signal)

        self._cache[cache_key] = bottlenecks
        return bottlenecks

    def analyze_batch(self, texts: list[str]) -> dict[str, list[BottleneckSignal]]:
        """Analyze multiple text signals.

        Returns:
            Dict mapping text (truncated) to list of detected bottlenecks
        """
        results = {}
        for text in texts:
            bottlenecks = self.analyze(text)
            key = text[:50]
            results[key] = bottlenecks
        return results

    def prioritize(
        self,
        bottlenecks: list[BottleneckSignal],
        top_n: int = 5,
    ) -> list[BottleneckSignal]:
        """Rank bottlenecks by composite score: automation_potential * leverage.

        Args:
            bottlenecks: List of detected bottlenecks
            top_n: Number of top results to return

        Returns:
            Sorted list, highest priority first
        """
        leverage_multiplier = {
            OperationalLeverage.HIGH: 2.0,
            OperationalLeverage.MEDIUM: 1.0,
            OperationalLeverage.LOW: 0.5,
        }

        def composite_score(b: BottleneckSignal) -> float:
            return b.automation_potential * leverage_multiplier[b.operational_leverage]

        return sorted(bottlenecks, key=composite_score, reverse=True)[:top_n]

    def _detect_gtm_function(self, text: str) -> GTMFunction:
        """Identify the primary GTM function affected."""
        scores = {}
        for gtm_func, patterns in self.GTM_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, text, re.I):
                    score += 1
            if score > 0:
                scores[gtm_func] = score

        if not scores:
            return GTMFunction.OPERATIONS  # default
        return max(scores, key=scores.get)

    def _extract_pain_points(self, text: str) -> list[str]:
        """Extract specific pain point categories from text."""
        found = []
        for pattern, label in self.PAIN_PATTERNS:
            if pattern.search(text):
                found.append(label)
        return found if found else ["general_friction"]

    def _detect_frequency(self, text: str) -> str:
        """Detect how frequently this bottleneck occurs."""
        chronic_indicators = [r"\b(always|constantly|repeatedly|every time|ongoing|chronic)\b"]
        recurring_indicators = [r"\b(often|frequently|regularly|usual|typically)\b"]

        for pattern in chronic_indicators:
            if re.search(pattern, text, re.I):
                return "chronic"
        for pattern in recurring_indicators:
            if re.search(pattern, text, re.I):
                return "recurring"
        return "sporadic"

    def _estimate_automation_potential(
        self,
        type_scores: dict[BottleneckType, float],
        text: str,
    ) -> float:
        """Estimate base automation potential (0-1).

        Logic:
        - INFORMATION_ASYMMETRY → high potential (AI can centralize and distribute)
        - MANUAL_HANDOFFF → high potential (data pipeline automation)
        - COORDINATION_COST → medium-high (AI orchestration)
        - DECISION_LATENCY → medium (AI can accelerate but often needs human sign-off)
        """
        if not type_scores:
            return 0.4

        type_base_scores = {
            BottleneckType.INFORMATION_ASYMMETRY: 0.82,
            BottleneckType.MANUAL_HANDOFFF: 0.78,
            BottleneckType.COORDINATION_COST: 0.68,
            BottleneckType.DECISION_LATENCY: 0.55,
        }

        # Weight by confidence
        weighted_sum = sum(
            type_base_scores.get(btype, 0.5) * score
            for btype, score in type_scores.items()
        )
        confidence_sum = sum(type_scores.values())
        base_score = weighted_sum / confidence_sum if confidence_sum > 0 else 0.5

        # Penalty for indicators that reduce automation potential
        penalty_indicators = [
            (r"\b(regulatory|compliant|legal|audit|sox)\b", 0.15),  # compliance friction
            (r"\b(creative|strategic|vision|brand)\b", 0.12),         # creative judgment
            (r"\b(culture|team.? dynamics|politics)\b", 0.10),      # org culture
            (r"\b(cannot automate|unavoidable human)\b", 0.20),      # explicit constraints
        ]
        for pattern, penalty in penalty_indicators:
            if re.search(pattern, text, re.I):
                base_score -= penalty

        return max(0.1, min(0.98, base_score))

    def _estimate_leverage(
        self,
        type_scores: dict[BottleneckType, float],
        gtm_function: GTMFunction,
        automation_potential: float,
    ) -> OperationalLeverage:
        """Estimate operational leverage of fixing this bottleneck.

        High leverage: bottlenecks that affect revenue-critical functions
        Medium leverage: bottlenecks that affect operational efficiency
        Low leverage: bottlenecks that are localized and marginal
        """
        # High leverage conditions
        if gtm_function in (GTMFunction.SALES, GTMFunction.CUSTOMER_SUCCESS):
            if automation_potential >= 0.6:
                return OperationalLeverage.HIGH

        if BottleneckType.DECISION_LATENCY in type_scores:
            if automation_potential >= 0.5:
                return OperationalLeverage.HIGH

        if gtm_function == GTMFunction.MARKETING and automation_potential >= 0.7:
            return OperationalLeverage.HIGH

        # Low leverage conditions
        if gtm_function == GTMFunction.FINANCE:
            return OperationalLeverage.MEDIUM  # high impact but slow

        if automation_potential <= 0.25:
            return OperationalLeverage.LOW

        return OperationalLeverage.MEDIUM

    def _detect_affected_stages(self, text: str) -> list[str]:
        """Detect which pipeline stages are affected."""
        stages = []
        stage_patterns = [
            (r"\b(top|early|awareness|funnel.?top)\b", "top_of_funnel"),
            (r"\b(mid|consideration|eval|comparison)\b", "mid_funnel"),
            (r"\b(bottom|closing|decision|proposal|negotiation)\b", "bottom_of_funnel"),
            (r"\b(post.?sale|onboard|renewal|upsell)\b", "post_sale"),
            (r"\b(full.?cycle|end.?to.?end|entire)\b", "full_cycle"),
        ]
        for pattern, stage in stage_patterns:
            if re.search(pattern, text, re.I):
                stages.append(stage)
        return stages if stages else ["unknown_stage"]

    def _map_to_patterns(
        self,
        type_scores: dict[BottleneckType, float],
        gtm_function: GTMFunction,
        automation_potential: float,
    ) -> list[str]:
        """Map detected bottlenecks to relevant redesign patterns."""
        patterns = []

        if gtm_function == GTMFunction.SALES:
            if BottleneckType.MANUAL_HANDOFFF in type_scores:
                patterns.append("autonomous_outbound")
            if BottleneckType.INFORMATION_ASYMMETRY in type_scores:
                patterns.append("real_time_lead_scoring")
            if BottleneckType.COORDINATION_COST in type_scores:
                patterns.append("dynamic_territory_management")

        elif gtm_function == GTMFunction.CUSTOMER_SUCCESS:
            if BottleneckType.DECISION_LATENCY in type_scores:
                patterns.append("ai_cs_triage")
            if BottleneckType.INFORMATION_ASYMMETRY in type_scores:
                patterns.append("predictive_churn")
            if BottleneckType.COORDINATION_COST in type_scores:
                patterns.append("outcome_based_renewal")

        elif gtm_function == GTMFunction.MARKETING:
            if BottleneckType.MANUAL_HANDOFFF in type_scores:
                patterns.append("automated_proposal_generation")
            if BottleneckType.INFORMATION_ASYMMETRY in type_scores:
                patterns.append("real_time_lead_scoring")

        if automation_potential >= 0.7:
            patterns.append("ai_assisted_negotiation")

        return patterns

    def _estimate_fte_savings(self, btype: BottleneckType, gtm_func: GTMFunction) -> Optional[float]:
        """Estimate FTE savings from automating this bottleneck (hours/week)."""
        base_savings = {
            BottleneckType.MANUAL_HANDOFFF: 12,
            BottleneckType.COORDINATION_COST: 8,
            BottleneckType.DECISION_LATENCY: 6,
            BottleneckType.INFORMATION_ASYMMETRY: 5,
        }
        multiplier = {
            GTMFunction.SALES: 1.5,
            GTMFunction.CUSTOMER_SUCCESS: 1.3,
            GTMFunction.MARKETING: 1.2,
            GTMFunction.OPERATIONS: 1.0,
        }
        base = base_savings.get(btype, 5)
        mult = multiplier.get(gtm_func, 1.0)
        return round(base * mult, 1)

    def _generate_id(self, text: str) -> str:
        """Generate a short deterministic ID from text."""
        import hashlib
        h = hashlib.md5(text.encode()).hexdigest()[:8]
        return f"bn_{h}"


def demo():
    """Run a demonstration of bottleneck detection."""
    detector = BottleneckDetector()

    test_signals = [
        "Sales reps spend 3 hours/day manually updating CRM fields from email threads. Lead enrichment is completely manual.",
        "CS managers review every cancellation risk manually. Churn predictions come two weeks too late.",
        "Marketing runs ABM campaigns manually - target list updates weekly, rep contacts people without knowing if they're in a campaign.",
        "Proposal generation takes 5 days because legal reviews every version. Sales has no visibility into approval status.",
        "Sales-ops constantly chasing reps for pipeline updates. Forecast accuracy is 50% because data is stale by Monday morning.",
    ]

    print("=" * 80)
    print("BOTTLENECK DETECTOR — DEMO")
    print("=" * 80)

    for signal_text in test_signals:
        bottlenecks = detector.analyze(signal_text, source="demo", category="workflow_pain")
        top = detector.prioritize(bottlenecks)

        print(f"\nSignal: {signal_text[:80]}...")
        print(f"Detected: {len(bottlenecks)} bottleneck(s)")
        for b in top:
            print(f"  [{b.bottleneck_type.value}] "
                  f"auto={b.automation_potential:.2f} "
                  f"leverage={b.operational_leverage.value} "
                  f"GTM={b.gtm_function.value} "
                  f"→ {b.suggested_patterns}")


if __name__ == "__main__":
    demo()