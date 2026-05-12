"""Escalation engine — determines when and how to escalate decisions.

Escalation is not a failure mode. It is a first-class feature of a healthy
AI-native organization: the system knows its own limits and routes to
the appropriate human at the right time.

The escalation engine is driven by three axes:
1. Confidence: How certain is the AI about its recommendation?
2. Risk: What is the downside if the AI is wrong?
3. Stakeholder availability: Who is available to receive the escalation?

The engine produces an escalation recommendation that includes:
- Whether to escalate
- Who to escalate to (escalation path)
- What information to provide to the human
- A suggested resolution
"""

from enum import Enum, auto
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


from .framework import (
    DecisionScope,
    RiskLevel,
    LifecycleStage,
    Decision,
    build_decision,
)


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EscalationTrigger(Enum):
    """Canonical reasons a decision gets escalated."""
    LOW_CONFIDENCE = auto()       # AI below confidence floor
    HIGH_RISK = auto()            # Risk level exceeds threshold
    DEAL_SIZE_EXCEEDS_LIMIT = auto()  # ACV above AI handling threshold
    MANUAL_OVERRIDE = auto()      # Human explicitly requests escalation
    POLICY_REQUIRED = auto()      # Policy mandates human review
    TIMEOUT = auto()              # Decision sat too long without resolution
    ANOMALY_DETECTED = auto()     # Signal pattern doesn't fit known categories


class EscalationUrgency(Enum):
    """How quickly does the human need to respond?"""
    LOW = auto()       # Async review within 24h
    MEDIUM = auto()     # Respond within 4h
    HIGH = auto()       # Immediate response needed (< 1h)
    CRITICAL = auto()   # Stop everything, resolve now


class EscalationStatus(Enum):
    """Lifecycle of an escalation."""
    PENDING = auto()        # Awaiting human response
    ACCEPTED = auto()       # Human acknowledged
    RESOLVED = auto()       # Human made a decision
    EXPIRED = auto()         # Human didn't respond in time
    CANCELLED = auto()       # Situation resolved without human


# ---------------------------------------------------------------------------
# Escalation Paths
# ---------------------------------------------------------------------------

@dataclass
class EscalationPath:
    """Defines the chain of reviewers for a given escalation.

    The path is traversed in order: if the primary reviewer doesn't
    acknowledge within the SLA window, it escalates to the next.
    """
    name: str
    stages: list[str]           # Ordered list: ["ai_agent", "team_lead", "vp"]
    sla_hours: list[float]      # Max hours at each stage before auto-escalating
                                # Must match len(stages)

    def get_reviewer(self, index: int) -> Optional[str]:
        if 0 <= index < len(self.stages):
            return self.stages[index]
        return None

    def next_reviewer(self, current_index: int) -> Optional[str]:
        return self.get_reviewer(current_index + 1)

    def total_sla_hours(self) -> float:
        return sum(self.sla_hours)


# Standard escalation paths
STANDARD_ESCALATION_PATHS: dict[str, EscalationPath] = {
    "sales_standard": EscalationPath(
        name="Sales Standard",
        stages=["ai_agent", "sales_rep", "team_lead", "vp_sales"],
        sla_hours=[0.0, 4.0, 8.0, 24.0],
    ),
    "sales_high_value": EscalationPath(
        name="Sales High Value (>$100k)",
        stages=["ai_agent", "sales_rep", "team_lead", "vp_sales", "cpo"],
        sla_hours=[0.0, 1.0, 2.0, 4.0, 24.0],
    ),
    "customer_success": EscalationPath(
        name="Customer Success",
        stages=["ai_agent", "cs_rep", "cs_manager", "vp_cs"],
        sla_hours=[0.0, 4.0, 8.0, 24.0],
    ),
    "legal_compliance": EscalationPath(
        name="Legal / Compliance",
        stages=["ai_agent", "legal_team", "general_counsel", "board"],
        sla_hours=[0.0, 24.0, 48.0, 168.0],
    ),
    "product_feedback": EscalationPath(
        name="Product Feedback",
        stages=["ai_agent", "product_manager", "product_director", "cto"],
        sla_hours=[0.0, 24.0, 48.0, 120.0],
    ),
}


# ---------------------------------------------------------------------------
# Escalation Triggers — Configuration
# ---------------------------------------------------------------------------

@dataclass
class EscalationTriggers:
    """Configuration thresholds that determine when to escalate.

    Tuned for a typical B2B SaaS with AI-native sales motion.
    Adjust to your org's risk tolerance.
    """
    # Confidence thresholds
    confidence_floor: float = 0.60       # Below this, must escalate
    confidence_review: float = 0.80      # Below this, human should review

    # Risk thresholds
    auto_escalate_risk: RiskLevel = RiskLevel.HIGH  # Above this, always escalate

    # Deal size thresholds (in ARR USD)
    ai_max_deal_size: float = 50000      # Above this, human must approve
    recommend_review_deal_size: float = 15000  # Above this, human should review

    # Timeout threshold
    decision_timeout_hours: float = 24.0  # Decisions older than this get auto-escalated

    # Signal anomaly
    unknown_signal_threshold: int = 3   # N unknown signals in a row → escalate


# ---------------------------------------------------------------------------
# Escalation Decision Record
# ---------------------------------------------------------------------------

@dataclass
class EscalationDecision:
    """Record of an escalation event."""
    id: str
    trigger: EscalationTrigger
    urgency: EscalationUrgency
    decision: Decision                      # The underlying decision being escalated
    path: EscalationPath
    current_stage: int = 0                  # Index into path.stages
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    status: EscalationStatus = EscalationStatus.PENDING
    resolution: Optional[str] = None        # "approved", "rejected", "modified"
    reviewer_notes: Optional[str] = None
    context_bundle: dict = field(default_factory=dict)  # All info to give the reviewer

    @property
    def current_reviewer(self) -> Optional[str]:
        return self.path.get_reviewer(self.current_stage)

    def is_expired(self) -> bool:
        if self.status != EscalationStatus.PENDING:
            return False
        if self.current_stage >= len(self.path.stages) - 1:
            return False  # Already at final stage
        sla = self.path.sla_hours[self.current_stage]
        elapsed = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return elapsed > sla

    def time_remaining_hours(self) -> float:
        if self.current_stage >= len(self.path.sla_hours):
            return 0.0
        sla = self.path.sla_hours[self.current_stage]
        elapsed = (datetime.utcnow() - self.created_at).total_seconds() / 3600
        return max(0.0, sla - elapsed)


# ---------------------------------------------------------------------------
# Escalation Engine
# ---------------------------------------------------------------------------

class EscalationEngine:
    """Evaluates decisions and determines if/where to escalate.

    Usage:
        engine = EscalationEngine()
        result = engine.evaluate(decision, context)
        if result.should_escalate:
            escalation = result.escalation
            # Route escalation to escalation.current_reviewer
    """

    def __init__(
        self,
        triggers: Optional[EscalationTriggers] = None,
        paths: Optional[dict[str, EscalationPath]] = None,
    ):
        self.triggers = triggers or EscalationTriggers()
        self.paths = paths or STANDARD_ESCALATION_PATHS

    def evaluate(
        self,
        decision: Decision,
        context: dict,
    ) -> "EscalationResult":
        """Evaluate a decision and return escalation recommendation.

        Args:
            decision: The Decision object to evaluate
            context: Dict with keys:
                - ai_confidence: float (0-1)
                - deal_size: float (optional, ARR USD)
                - signals: list of signal categories seen recently
                - lifecycle: LifecycleStage
                - stakeholder_availability: dict of reviewer → bool

        Returns:
            EscalationResult with should_escalate, urgency, path, and reason
        """
        reasons = []
        should_escalate = False
        urgency = EscalationUrgency.LOW
        trigger = None

        # 1. Confidence check
        ai_confidence = context.get("ai_confidence", 0.5)
        if ai_confidence < self.triggers.confidence_floor:
            should_escalate = True
            trigger = EscalationTrigger.LOW_CONFIDENCE
            reasons.append(f"AI confidence {ai_confidence:.0%} below floor {self.triggers.confidence_floor:.0%}")
            if ai_confidence < 0.40:
                urgency = EscalationUrgency.HIGH

        # 2. Risk check
        risk = context.get("risk", RiskLevel.LOW)
        if self._risk_meets_threshold(risk, self.triggers.auto_escalate_risk):
            should_escalate = True
            if trigger is None:
                trigger = EscalationTrigger.HIGH_RISK
            reasons.append(f"Risk level {risk.name} exceeds auto-escalate threshold")
            if risk == RiskLevel.CRITICAL:
                urgency = EscalationUrgency.CRITICAL
            elif risk == RiskLevel.HIGH:
                urgency = max(urgency, EscalationUrgency.HIGH)

        # 3. Deal size check
        deal_size = context.get("deal_size")
        if deal_size is not None:
            if deal_size > self.triggers.ai_max_deal_size:
                should_escalate = True
                if trigger is None:
                    trigger = EscalationTrigger.DEAL_SIZE_EXCEEDS_LIMIT
                reasons.append(f"Deal size ${deal_size:,.0f} exceeds AI max ${self.triggers.ai_max_deal_size:,.0f}")
                urgency = max(urgency, EscalationUrgency.MEDIUM)
            elif deal_size > self.triggers.recommend_review_deal_size:
                # Not a hard escalation, but flag for review
                reasons.append(f"Deal size ${deal_size:,.0f} warrants human review (${self.triggers.recommend_review_deal_size:,.0f} threshold)")

        # 4. Timeout check
        if decision.created_at:
            elapsed_hours = (datetime.utcnow() - decision.created_at).total_seconds() / 3600
            if elapsed_hours > self.triggers.decision_timeout_hours:
                should_escalate = True
                if trigger is None:
                    trigger = EscalationTrigger.TIMEOUT
                reasons.append(f"Decision unresolved for {elapsed_hours:.1f}h, exceeds {self.triggers.decision_timeout_hours}h timeout")
                urgency = max(urgency, EscalationUrgency.MEDIUM)

        # 5. Anomaly check — too many unknown signals in sequence
        signals = context.get("signals", [])
        unknown_signals = [s for s in signals if context.get(f"unknown_{s}", False)]
        if len(unknown_signals) >= self.triggers.unknown_signal_threshold:
            should_escalate = True
            if trigger is None:
                trigger = EscalationTrigger.ANOMALY_DETECTED
            reasons.append(f"{len(unknown_signals)} unknown signals in sequence, exceeds threshold")
            urgency = max(urgency, EscalationUrgency.MEDIUM)

        # 6. Manual override
        if context.get("manual_escalation_requested", False):
            should_escalate = True
            if trigger is None:
                trigger = EscalationTrigger.MANUAL_OVERRIDE
            reasons.append("Human explicitly requested escalation")
            urgency = max(urgency, EscalationUrgency.MEDIUM)

        # Determine path based on lifecycle and risk
        path = self._select_path(
            decision.lifecycle,
            risk,
            deal_size,
            decision.decision_type,
        )

        # Build result
        if should_escalate and trigger:
            escalation = EscalationDecision(
                id=f"esc_{decision.id}_{int(datetime.utcnow().timestamp())}",
                trigger=trigger,
                urgency=urgency,
                decision=decision,
                path=path,
                context_bundle={
                    "ai_confidence": ai_confidence,
                    "deal_size": deal_size,
                    "risk": risk.name,
                    "signals": signals,
                    "reasons": reasons,
                    "recommendation": decision.recommendation,
                },
            )
        else:
            escalation = None

        return EscalationResult(
            should_escalate=should_escalate,
            trigger=trigger,
            urgency=urgency,
            escalation=escalation,
            reasons=reasons,
            path=path,
        )

    def _risk_meets_threshold(self, risk: RiskLevel, threshold: RiskLevel) -> bool:
        risk_order = {RiskLevel.TRIVIAL: 0, RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3, RiskLevel.CRITICAL: 4}
        return risk_order.get(risk, 0) >= risk_order.get(threshold, 0)

    def _select_path(
        self,
        lifecycle: LifecycleStage,
        risk: RiskLevel,
        deal_size: Optional[float],
        decision_type: str,
    ) -> EscalationPath:
        """Select the appropriate escalation path."""
        # High value deal override
        if deal_size is not None and deal_size > 100000:
            return self.paths["sales_high_value"]

        # Lifecycle-based defaults
        if lifecycle in (LifecycleStage.CLOSE, LifecycleStage.EXPAND):
            return self.paths["sales_standard"]
        if lifecycle == LifecycleStage.RENEW:
            return self.paths["customer_success"]
        if decision_type in ("contract_terms", "legal_review", "compliance_check"):
            return self.paths["legal_compliance"]
        if "product" in decision_type or "feedback" in decision_type:
            return self.paths["product_feedback"]

        return self.paths["sales_standard"]


@dataclass
class EscalationResult:
    """Result of evaluating a decision for escalation."""
    should_escalate: bool
    trigger: Optional[EscalationTrigger]
    urgency: EscalationUrgency
    escalation: Optional[EscalationDecision]
    reasons: list[str]
    path: EscalationPath

    @property
    def summary(self) -> str:
        if not self.should_escalate:
            return "No escalation needed — AI can handle this."
        lines = [f"Escalation recommended: {self.trigger.name if self.trigger else 'unknown'}"]
        lines += [f"  Urgency: {self.urgency.name}"]
        lines += [f"  Path: {' → '.join(self.path.stages)}"]
        if self.reasons:
            lines.append("  Reasons:")
            for r in self.reasons:
                lines.append(f"    - {r}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helper: Create escalated decision from analysis
# ---------------------------------------------------------------------------

def create_escalation(
    decision: Decision,
    trigger: EscalationTrigger,
    urgency: EscalationUrgency,
    ai_confidence: float,
    deal_size: Optional[float] = None,
    risk: RiskLevel = RiskLevel.MEDIUM,
    signals: Optional[list[str]] = None,
) -> EscalationDecision:
    """Create an escalation record from a decision and context.

    Convenience helper for building escalations in the signal pipeline.
    """
    engine = EscalationEngine()
    context = {
        "ai_confidence": ai_confidence,
        "deal_size": deal_size,
        "risk": risk,
        "signals": signals or [],
    }
    result = engine.evaluate(decision, context)
    if result.escalation:
        return result.escalation
    raise ValueError("create_escalation called but evaluation shows no escalation needed")