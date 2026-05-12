"""Decision analyzer — extracts decision implications from signals.

Given a stream of signals (market events, operational data, customer
interactions), the analyzer determines:

1. Which decisions are implied by the signal cluster?
2. What is the urgency and risk of each implied decision?
3. What information does the decision need to be made well?
4. Should this signal cluster trigger a single decision or a cascade?

This module sits between signal collection and decision execution.
It is the "sense-making" layer that turns raw signals into actionable
decisions with appropriate routing and urgency.

The analyzer does NOT make decisions — it prepares decision briefs
for either AI or human decision-makers.
"""

from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
import re

from .framework import (
    Decision,
    DecisionScope,
    RiskLevel,
    LifecycleStage,
    DecisionSpeed,
    DecisionRightsMatrix,
    DecisionRouter,
    RoutingRule,
    build_decision,
    LIFECYCLE_DECISION_POINTS,
)
from .escalation import (
    EscalationEngine,
    EscalationTriggers,
    EscalationResult,
)


# ---------------------------------------------------------------------------
# Decision Brief — the output of analysis
# ---------------------------------------------------------------------------

@dataclass
class DecisionBrief:
    """A prepared brief for a decision-maker (AI or human).

    Contains everything needed to make a high-quality decision:
    the what, why, urgency, risks, options, and supporting context.
    """
    id: str
    decision_type: str
    lifecycle: LifecycleStage
    scope: DecisionScope
    urgency: str                   # "real_time", "fast", "standard", "deliberate"
    risk: RiskLevel
    decision_question: str          # The core question to answer
    options: list[str]             # Available options (AI-generated)
    recommendation: Optional[str]  # AI's recommendation (if scoped)
    confidence: float              # AI confidence in recommendation (0-1)
    context: dict                  # Supporting data for the decision
    signals_used: list[str]        # Which signals informed this brief
    created_at: datetime = field(default_factory=datetime.utcnow)
    decision_points_triggered: list[str] = field(default_factory=list)  # gate IDs
    escalation_recommended: bool = False
    escalation_urgency: Optional[str] = None
    escalation_path: Optional[str] = None
    notes: Optional[str] = None

    def to_decision(self, decided_by: str = "ai_agent") -> Decision:
        return build_decision(
            decision_type=self.decision_type,
            lifecycle=self.lifecycle,
            scope=self.scope,
            ai_recommendation=self.recommendation,
            decided_by=decided_by,
        )

    def to_human_brief(self) -> str:
        """Format as a readable brief for a human reviewer."""
        lines = [
            f"## Decision Brief: {self.decision_type}",
            f"**Lifecycle:** {self.lifecycle.name} | **Risk:** {self.risk.name}",
            f"**Urgency:** {self.urgency}",
            f"**Confidence:** {self.confidence:.0%}",
            "",
            f"### Decision Question",
            self.decision_question,
            "",
            f"### Options",
        ]
        for i, opt in enumerate(self.options, 1):
            lines.append(f"{i}. {opt}")
        if self.recommendation:
            lines.extend(["", f"### AI Recommendation", f"**{self.recommendation}**"])
        lines.extend([
            "",
            "### Supporting Context",
        ])
        for k, v in self.context.items():
            lines.append(f"- **{k}:** {v}")
        if self.escalation_recommended:
            lines.extend([
                "",
                f"⚠️ **Escalation Recommended:** {self.escalation_urgency} — path: {self.escalation_path}",
            ])
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Implied Decision — internal structure during analysis
# ---------------------------------------------------------------------------

@dataclass
class ImpliedDecision:
    """A decision that is implied by signal analysis.

    Internal structure used during the analysis pipeline.
    Converted to DecisionBrief before presenting to a decision-maker.
    """
    decision_type: str
    lifecycle: LifecycleStage
    trigger_signals: list[str]
    trigger_texts: list[str]
    urgency: DecisionSpeed
    risk: RiskLevel
    deal_size: Optional[float] = None
    ai_confidence: float = 0.5
    context: dict = field(default_factory=dict)
    options: list[str] = field(default_factory=list)
    recommendation: Optional[str] = None


# ---------------------------------------------------------------------------
# Signal-to-Decision Mapping
# ---------------------------------------------------------------------------

# Maps signal category patterns → implied decision types
# This is the operational knowledge base of the analyzer

SIGNAL_DECISION_MAPPING: list[tuple[list[str], str, LifecycleStage]] = [
    # (trigger patterns, decision_type, lifecycle)
    (["competitor_pricing_change", "competitor_discount"], "competitor_response", LifecycleStage.CLOSE),
    (["budget_confirmed", "authority_confirmed"], "deal_qualification", LifecycleStage.QUALIFY),
    (["champion_change", "economic_buyer_change"], "stakeholder_shift", LifecycleStage.QUALIFY),
    (["pricing_objection", "discount_request"], "pricing_approval", LifecycleStage.CLOSE),
    (["legal_review_requested", "contract_redlines"], "contract_approval", LifecycleStage.CLOSE),
    (["closed_won", "contract_signed"], "close_confirmation", LifecycleStage.CLOSE),
    (["usage_drop", "health_score_declining"], "churn_intervention", LifecycleStage.RENEW),
    (["renewal_date_approaching"], "renewal_preparation", LifecycleStage.RENEW),
    (["expansion_signal", "upsell_opportunity"], "expansion_approval", LifecycleStage.EXPAND),
    (["new_competitor_entered", "market_shift"], "market_entry_decision", LifecycleStage.PROSPECT),
    (["lead_surfaced", "inbound_inquiry"], "lead_scoring", LifecycleStage.PROSPECT),
    (["demo_completed", "poc_completed"], "evaluation_outcome", LifecycleStage.QUALIFY),
    (["objection_raised", "pricing_pushback"], "objection_handling", LifecycleStage.CLOSE),
]


# ---------------------------------------------------------------------------
# Decision Analyzer
# ---------------------------------------------------------------------------

class DecisionAnalyzer:
    """Analyzes signals and produces decision briefs.

    The analyzer processes signal clusters (multiple signals seen together)
    and extracts the implied decisions. It evaluates scope, urgency, and
    risk, then produces briefs ready for AI or human decision-making.

    Usage:
        analyzer = DecisionAnalyzer()
        briefs = analyzer.analyze_signals(signals)
        for brief in briefs:
            if brief.escalation_recommended:
                route_to_human(brief)
            else:
                execute_ai_decision(brief)
    """

    def __init__(
        self,
        rights_matrix: Optional[DecisionRightsMatrix] = None,
        router: Optional[DecisionRouter] = None,
        escalation_engine: Optional[EscalationEngine] = None,
    ):
        self.rights = rights_matrix or DecisionRightsMatrix()
        self.router = router or DecisionRouter()
        self.escalation_engine = escalation_engine or EscalationEngine()

    def analyze_signals(
        self,
        signals: list[dict],
        lifecycle: Optional[LifecycleStage] = None,
        deal_size: Optional[float] = None,
    ) -> list[DecisionBrief]:
        """Analyze a cluster of signals and produce decision briefs.

        Args:
            signals: List of dicts with keys:
                - category: str (signal type)
                - text: str (raw signal text)
                - metadata: dict (optional additional context)
            lifecycle: Override lifecycle stage for all signals
            deal_size: Override deal size for all signals

        Returns:
            List of DecisionBrief objects, one per implied decision
        """
        if not signals:
            return []

        # Determine lifecycle from signals if not provided
        lifecycle = lifecycle or self._infer_lifecycle(signals)

        # Extract implied decisions from signal cluster
        implied = self._extract_implied_decisions(signals, lifecycle)

        # Convert to briefs with scope and escalation evaluation
        briefs = []
        for imp in implied:
            brief = self._build_brief(imp, signals, deal_size)
            briefs.append(brief)

        return briefs

    def analyze_single_signal(
        self,
        signal_category: str,
        signal_text: str,
        metadata: Optional[dict] = None,
        lifecycle: Optional[LifecycleStage] = None,
        deal_size: Optional[float] = None,
    ) -> list[DecisionBrief]:
        """Analyze a single signal and produce any implied decision briefs."""
        return self.analyze_signals(
            signals=[{"category": signal_category, "text": signal_text, "metadata": metadata or {}}],
            lifecycle=lifecycle,
            deal_size=deal_size,
        )

    def _infer_lifecycle(self, signals: list[dict]) -> LifecycleStage:
        """Infer lifecycle stage from signal categories."""
        category_lifecycle_map = {
            "lead_surfaced": LifecycleStage.PROSPECT,
            "demo_completed": LifecycleStage.QUALIFY,
            "proposal_sent": LifecycleStage.CLOSE,
            "closed_won": LifecycleStage.CLOSE,
            "closed_lost": LifecycleStage.CLOSE,
            "usage_drop": LifecycleStage.RENEW,
            "renewal_date_approaching": LifecycleStage.RENEW,
            "expansion_signal": LifecycleStage.EXPAND,
            "upsell_opportunity": LifecycleStage.EXPAND,
        }
        for sig in signals:
            cat = sig.get("category", "")
            if cat in category_lifecycle_map:
                return category_lifecycle_map[cat]
        return LifecycleStage.PROSPECT

    def _extract_implied_decisions(
        self,
        signals: list[dict],
        lifecycle: LifecycleStage,
    ) -> list[ImpliedDecision]:
        """Map signal patterns to implied decisions."""
        categories = {s.get("category", "") for s in signals}
        texts = [s.get("text", "") for s in signals]
        metadata = signals[0].get("metadata", {}) if signals else {}

        implied = []

        for patterns, decision_type, dec_lifecycle in SIGNAL_DECISION_MAPPING:
            if any(cat in categories for cat in patterns):
                # Check if router has a rule for this
                routed = self.router.route(
                    signal_category=signals[0].get("category", ""),
                    metadata={
                        "lifecycle": lifecycle,
                        "deal_size": metadata.get("deal_size"),
                    },
                )
                # Also check direct mapping
                if decision_type not in routed:
                    routed.append(decision_type)

                for rt in routed:
                    speed = self._infer_speed(rt, metadata)
                    risk = self._infer_risk(rt, metadata)
                    confidence = self._infer_confidence(rt, metadata, texts)

                    imp = ImpliedDecision(
                        decision_type=rt,
                        lifecycle=lifecycle or dec_lifecycle,
                        trigger_signals=list(categories),
                        trigger_texts=texts,
                        urgency=speed,
                        risk=risk,
                        deal_size=metadata.get("deal_size"),
                        ai_confidence=confidence,
                        context={
                            "signal_categories": list(categories),
                            "metadata": metadata,
                            "signal_count": len(signals),
                        },
                    )
                    implied.append(imp)

        return implied

    def _build_brief(
        self,
        imp: ImpliedDecision,
        signals: list[dict],
        deal_size_override: Optional[float] = None,
    ) -> DecisionBrief:
        """Build a DecisionBrief from an ImpliedDecision."""
        deal_size = deal_size_override or imp.deal_size

        # Resolve decision scope
        scope = self.rights.resolve_scope(
            lifecycle=imp.lifecycle,
            risk=imp.risk,
            ai_confidence=imp.ai_confidence,
            deal_size=deal_size,
        )

        # Evaluate escalation
        decision = imp.to_decision() if hasattr(imp, "to_decision") else build_decision(
            decision_type=imp.decision_type,
            lifecycle=imp.lifecycle,
            scope=scope,
        )

        escalation_result = self.escalation_engine.evaluate(
            decision,
            context={
                "ai_confidence": imp.ai_confidence,
                "deal_size": deal_size,
                "risk": imp.risk,
                "signals": imp.trigger_signals,
            },
        )

        # Generate options based on decision type
        options = self._generate_options(imp.decision_type, imp.context)

        # Generate recommendation if AI can decide
        recommendation = None
        if scope == DecisionScope.AI_FULLY_AUTONOMOUS and imp.ai_confidence >= 0.80:
            recommendation = self._generate_recommendation(imp, options)

        urgency_str = {
            DecisionSpeed.REAL_TIME: "real_time",
            DecisionSpeed.FAST: "fast",
            DecisionSpeed.STANDARD: "standard",
            DecisionSpeed.DELIBERATE: "deliberate",
            DecisionSpeed.ESCALATED: "deliberate",
        }.get(imp.urgency, "standard")

        brief = DecisionBrief(
            id=f"brief_{imp.decision_type}_{int(datetime.utcnow().timestamp())}",
            decision_type=imp.decision_type,
            lifecycle=imp.lifecycle,
            scope=scope,
            urgency=urgency_str,
            risk=imp.risk,
            decision_question=self._build_question(imp),
            options=options,
            recommendation=recommendation,
            confidence=imp.ai_confidence,
            context=imp.context,
            signals_used=imp.trigger_signals,
            decision_points_triggered=self._find_decision_points(imp.lifecycle, imp.decision_type),
            escalation_recommended=escalation_result.should_escalate,
            escalation_urgency=escalation_result.urgency.name.lower() if escalation_result.should_escalate else None,
            escalation_path=" → ".join(escalation_result.path.stages) if escalation_result.should_escalate else None,
        )

        return brief

    def _infer_speed(self, decision_type: str, metadata: dict) -> DecisionSpeed:
        speed_map = {
            "lead_scoring": DecisionSpeed.REAL_TIME,
            "competitor_response": DecisionSpeed.FAST,
            "pricing_approval": DecisionSpeed.STANDARD,
            "deal_qualification": DecisionSpeed.STANDARD,
            "contract_approval": DecisionSpeed.DELIBERATE,
            "churn_intervention": DecisionSpeed.FAST,
            "expansion_approval": DecisionSpeed.DELIBERATE,
        }
        return speed_map.get(decision_type, DecisionSpeed.STANDARD)

    def _infer_risk(self, decision_type: str, metadata: dict) -> RiskLevel:
        risk_map = {
            "lead_scoring": RiskLevel.TRIVIAL,
            "competitor_response": RiskLevel.LOW,
            "pricing_approval": RiskLevel.MEDIUM,
            "deal_qualification": RiskLevel.LOW,
            "contract_approval": RiskLevel.HIGH,
            "churn_intervention": RiskLevel.MEDIUM,
            "expansion_approval": RiskLevel.HIGH,
        }
        override = metadata.get("risk_override")
        if override:
            try:
                return RiskLevel[override.upper()]
            except KeyError:
                pass
        return risk_map.get(decision_type, RiskLevel.MEDIUM)

    def _infer_confidence(self, decision_type: str, metadata: dict, texts: list[str]) -> float:
        # In production, this would call an LLM to assess
        # confidence based on signal quality. Here we use heuristics.
        base = 0.70
        signal_count = len(texts)
        if signal_count >= 3:
            base += 0.10
        if metadata.get("source_quality") == "high":
            base += 0.10
        # Discount for short texts
        avg_len = sum(len(t) for t in texts) / max(len(texts), 1)
        if avg_len < 50:
            base -= 0.10
        return max(0.30, min(0.95, base))

    def _generate_options(self, decision_type: str, context: dict) -> list[str]:
        """Generate available options for a decision type."""
        options_map = {
            "competitor_response": [
                "Match competitor pricing with volume commitment",
                "Hold current pricing, offer additional value",
                "Increase discount temporarily to win deal",
                "No action — monitor competitor move",
            ],
            "deal_qualification": [
                "Advance to proposal stage",
                "Continue nurturing with additional content",
                "Disqualify — not ICP fit",
                "Request more information before deciding",
            ],
            "pricing_approval": [
                "Approve requested discount as-is",
                "Approve partial discount (50%)",
                "Require approval up one level",
                "Decline discount request",
            ],
            "churn_intervention": [
                "Proactive outreach with success plan",
                "Trigger executive sponsor engagement",
                "Schedule renewal call with discount offer",
                "Flag for customer success manager review",
            ],
            "expansion_approval": [
                "Approve expansion as proposed",
                "Approve with modified scope",
                "Require demo/review before approval",
                "Defer to next planning cycle",
            ],
            "lead_scoring": [
                "Route to A-level rep immediately",
                "Route to B-level rep with 24h follow-up",
                "Add to nurture sequence",
                "Archive — not a real opportunity",
            ],
            "contract_approval": [
                "Approve standard terms",
                "Approve with redlines (specify)",
                "Require legal review",
                "Decline — terms unacceptable",
            ],
        }
        return options_map.get(decision_type, ["Option A", "Option B", "Escalate to human"])

    def _generate_recommendation(self, imp: ImpliedDecision, options: list[str]) -> str:
        """Generate a recommendation string.

        In production, this would call an LLM with the full brief.
        Here we use simple heuristics.
        """
        if imp.ai_confidence >= 0.85:
            return f"Proceed with {options[0]} (confidence {imp.ai_confidence:.0%})"
        elif imp.ai_confidence >= 0.70:
            return f"Recommend {options[0]}, but review recommended"
        return f"Options: {' / '.join(options[:2])} — human review advised"

    def _build_question(self, imp: ImpliedDecision) -> str:
        """Build the core decision question."""
        questions = {
            "competitor_response": "How should we respond to the competitor pricing change?",
            "deal_qualification": "Should we advance this deal to proposal stage?",
            "pricing_approval": "Should we approve the requested discount?",
            "churn_intervention": "What intervention is appropriate given the usage drop?",
            "expansion_approval": "Should we approve the expansion opportunity?",
            "lead_scoring": "How should we prioritize and route this lead?",
            "contract_approval": "Should we accept the contract terms as-is?",
        }
        return questions.get(imp.decision_type, f"What action should we take on {imp.decision_type}?")

    def _find_decision_points(self, lifecycle: LifecycleStage, decision_type: str) -> list[str]:
        """Find which lifecycle decision points this decision triggers."""
        triggered = []
        for dp in LIFECYCLE_DECISION_POINTS:
            if dp.lifecycle == lifecycle:
                # Match by decision type keyword
                if any(kw in decision_type for kw in dp.name.lower().split()):
                    triggered.append(dp.id)
        return triggered

    def to_decision(self, brief: DecisionBrief, decided_by: str) -> Decision:
        """Convert a DecisionBrief to a Decision record."""
        return brief.to_decision(decided_by=decided_by)


# ---------------------------------------------------------------------------
# Convenience: Quick analysis from signal dict
# ---------------------------------------------------------------------------

def analyze_signal(
    category: str,
    text: str,
    metadata: Optional[dict] = None,
    lifecycle: Optional[LifecycleStage] = None,
    deal_size: Optional[float] = None,
) -> list[DecisionBrief]:
    """One-liner to analyze a signal and get briefs."""
    analyzer = DecisionAnalyzer()
    return analyzer.analyze_single_signal(
        signal_category=category,
        signal_text=text,
        metadata=metadata,
        lifecycle=lifecycle,
        deal_size=deal_size,
    )