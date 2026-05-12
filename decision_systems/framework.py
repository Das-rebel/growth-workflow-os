"""Decision architecture framework for AI-native organizations.

Handles how decisions are made, routed, and executed when AI agents are first-class actors.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class DecisionType(Enum):
    """Categories of decisions in AI-native GTM."""
    PROSPECTING = "prospecting"
    QUALIFICATION = "qualification"
    PRICING = "pricing"
    ESCALATION = "escalation"
    RENEWAL = "renewal"
    CHURN = "churn"
    TERRITORY = "territory"
    RESOURCE_ALLOCATION = "resource_allocation"


class DecisionAgent(Enum):
    """Who makes the decision."""
    AI_AGENT = "ai_agent"
    HUMAN_AGENT = "human_agent"
    HYBRID = "hybrid"
    ESCALATE = "escalate"


@dataclass
class LifecycleDecision:
    """A decision point in the GTM lifecycle."""
    stage: str
    decision_text: str
    options: list[str]
    ai_decision_example: str
    human_decision_example: str
    escalation_criteria: str


@dataclass
class DecisionRule:
    """A rule for who decides and under what conditions."""
    decision_type: DecisionType
    trigger_condition: str
    decision_maker: DecisionAgent
    confidence_threshold: float
    deal_size_threshold: float
    automation_ceiling: float
    escalation_path: list[str]
    rationale: str


# Build DECISION_FRAMEWORK incrementally to avoid enum access issues
_decision_rules: dict = {}


def _make_rule(
    decision_type: DecisionType,
    trigger_condition: str,
    decision_maker: DecisionAgent,
    confidence_threshold: float,
    deal_size_threshold: float,
    automation_ceiling: float,
    escalation_path: list[str],
    rationale: str,
) -> DecisionRule:
    return DecisionRule(
        decision_type=decision_type,
        trigger_condition=trigger_condition,
        decision_maker=decision_maker,
        confidence_threshold=confidence_threshold,
        deal_size_threshold=deal_size_threshold,
        automation_ceiling=automation_ceiling,
        escalation_path=escalation_path,
        rationale=rationale,
    )


# PROSPECTING
_prospecting_rule = _make_rule(
    DecisionType.PROSPECTING,
    "New account identified in target ICP",
    DecisionAgent.AI_AGENT,
    0.75,
    float("inf"),
    0.95,
    ["ai_agent"],
    "Prospecting is high-volume, low-stakes. AI agents can handle 95% autonomously.",
)
_decision_rules[DecisionType.PROSPECTING] = _prospecting_rule

# QUALIFICATION
_qualification_rule = _make_rule(
    DecisionType.QUALIFICATION,
    "Initial outreach response received",
    DecisionAgent.AI_AGENT,
    0.80,
    50000,
    0.85,
    ["ai_agent", "ae"],
    "AI qualifies at high accuracy for price signals, human needed for complex evaluations.",
)
_decision_rules[DecisionType.QUALIFICATION] = _qualification_rule

# PRICING
_pricing_rule = _make_rule(
    DecisionType.PRICING,
    "Proposal generation triggered",
    DecisionAgent.HYBRID,
    0.90,
    0,
    0.40,
    ["ae", "vp_sales"],
    "Pricing requires business context, relationship, and negotiation. AI suggests, human decides.",
)
_decision_rules[DecisionType.PRICING] = _pricing_rule

# ESCALATION
_escalation_rule = _make_rule(
    DecisionType.ESCALATION,
    "Customer requests human contact or complex objection",
    DecisionAgent.HUMAN_AGENT,
    0.0,
    0,
    0.0,
    ["ae", "vp", "exec"],
    "Escalation is definitionally human-handled. AI should flag and route, not resolve.",
)
_decision_rules[DecisionType.ESCALATION] = _escalation_rule

# RENEWAL
_renewal_rule = _make_rule(
    DecisionType.RENEWAL,
    "Renewal date approaches (90 days out)",
    DecisionAgent.AI_AGENT,
    0.85,
    30000,
    0.75,
    ["ai_agent", "csm"],
    "AI can handle straightforward renewals. Complex accounts need CSM relationship.",
)
_decision_rules[DecisionType.RENEWAL] = _renewal_rule

# CHURN
_churn_rule = _make_rule(
    DecisionType.CHURN,
    "Health score drops below threshold",
    DecisionAgent.HYBRID,
    0.80,
    50000,
    0.65,
    ["ai_agent", "csm", "vp_cs"],
    "AI detects churn risk, human CSM decides intervention strategy.",
)
_decision_rules[DecisionType.CHURN] = _churn_rule

# TERRITORY
_territory_rule = _make_rule(
    DecisionType.TERRITORY,
    "Quarter start or territory rebalance needed",
    DecisionAgent.HYBRID,
    0.85,
    0,
    0.70,
    ["rev_ops", "vp_sales"],
    "AI can optimize territory assignments but humans must approve final distribution.",
)
_decision_rules[DecisionType.TERRITORY] = _territory_rule

# RESOURCE_ALLOCATION
_resource_rule = _make_rule(
    DecisionType.RESOURCE_ALLOCATION,
    "Resource request from sales or CS",
    DecisionAgent.HUMAN_AGENT,
    0.0,
    0,
    0.30,
    ["rev_ops", "vp"],
    "Resource allocation requires strategic context AI doesn't have.",
)
_decision_rules[DecisionType.RESOURCE_ALLOCATION] = _resource_rule


@dataclass
class DecisionRule:
    """A rule for who decides and under what conditions."""
    decision_type: DecisionType
    trigger_condition: str
    decision_maker: DecisionAgent
    confidence_threshold: float  # For AI decisions, minimum confidence required
    deal_size_threshold: float  # Above this, escalate to human
    automation_ceiling: float  # Max % AI can decide autonomously
    escalation_path: list[str]  # [agent, team_lead, vp, exec]
    rationale: str


DECISION_FRAMEWORK: dict = {
    DecisionType.PROSPECTING: _prospecting_rule,
    DecisionType.QUALIFICATION: _qualification_rule,
    DecisionType.PRICING: _pricing_rule,
    DecisionType.ESCALATION: _escalation_rule,
    DecisionType.RENEWAL: _renewal_rule,
    DecisionType.CHURN: _churn_rule,
    DecisionType.TERRITORY: _territory_rule,
    DecisionType.RESOURCE_ALLOCATION: _resource_rule,
}

LIFECYCLE_DECISIONS: list[LifecycleDecision] = [
    LifecycleDecision(
        stage="prospect",
        decision_text="Which accounts to target in a given week?",
        options=["AI-driven ICP scoring", "Human gut feel", "Static target list"],
        ai_decision_example="AI scores 500 accounts against ICP, ranks top 50 for agent outreach this week",
        human_decision_example="AE reviews AI output, approves or adjusts based on local market knowledge",
        escalation_criteria="High-value account not in AI's target list",
    ),
    LifecycleDecision(
        stage="qualify",
        decision_text="Is this opportunity worth pursuing?",
        options=["AI disqualifies based on signals", "AI advances to demo", "Human qualifies"],
        ai_decision_example="AI analyzes response pattern, budget signals, authority indicators → disqualify or advance",
        human_decision_example="AE reviews AI qualification, calls prospect if uncertain",
        escalation_criteria="Complex multi-stakeholder deal that AI can't fully assess",
    ),
    LifecycleDecision(
        stage="demo",
        decision_text="What demo content to show?",
        options=["AI personalizes demo for prospect", "Static demo deck", "Human-curated demo"],
        ai_decision_example="AI analyzes prospect's tech stack, industry, role → selects relevant product features",
        human_decision_example="AE reviews AI demo choice, adds personal anecdotes or competitive positioning",
        escalation_criteria="Executive-level demo that requires senior AE presence",
    ),
    LifecycleDecision(
        stage="proposal",
        decision_text="What pricing and packaging to propose?",
        options=["AI generates proposal within bounds", "Fixed pricing template", "Human-crafted proposal"],
        ai_decision_example="AI calculates dynamic pricing based on deal size, competition, relationship",
        human_decision_example="AE adjusts AI proposal for strategic deals, applies discounts",
        escalation_criteria="Large deal (>$100k) or competitive situation requiring VP approval",
    ),
    LifecycleDecision(
        stage="close",
        decision_text="Ready to close or need more nurturing?",
        options=["AI recommends close timing", "AE gut feeling", "Fixed close date"],
        ai_decision_example="AI analyzes engagement signals, objection resolution, competitor mentions → recommend close",
        human_decision_example="AE considers relationship, intuition, and AI recommendation",
        escalation_criteria="Customer requested executive sponsor involvement for close",
    ),
    LifecycleDecision(
        stage="renew",
        decision_text="Auto-renew, negotiate, or start exit process?",
        options=["AI recommends renewal action", "CSM decides based on health", "Automatic renewal"],
        ai_decision_example="AI calculates renewal risk, CS health, expansion potential → recommend action",
        human_decision_example="CSM reviews AI recommendation, executes renewal conversation",
        escalation_criteria="Churn risk score > 0.7 → CSM + VP CS escalation",
    ),
]


def should_escalate(
    decision_type: DecisionType,
    ai_confidence: float,
    deal_size: float,
    complexity_score: float = 0.5,
) -> tuple[bool, str]:
    """Determine if a decision should escalate from AI to human.

    Args:
        decision_type: Type of decision
        ai_confidence: AI's confidence score (0-1)
        deal_size: Deal size in dollars
        complexity_score: How complex the situation is (0-1)

    Returns:
        (should_escalate, reason)
    """
    rule = DECISION_FRAMEWORK.get(decision_type)
    if not rule:
        return True, f"Unknown decision type: {decision_type}"

    # Check confidence threshold
    if ai_confidence < rule.confidence_threshold:
        return True, f"AI confidence {ai_confidence:.0%} below threshold {rule.confidence_threshold:.0%}"

    # Check deal size threshold
    if deal_size > rule.deal_size_threshold:
        return True, f"Deal size ${deal_size:,.0f} exceeds human threshold ${rule.deal_size_threshold:,.0f}"

    # Check complexity
    if complexity_score > 0.8:
        return True, f"Complexity score {complexity_score:.0%} too high for autonomous AI decision"

    # Check if decision type is inherently human
    if rule.decision_maker == DecisionAgent.HUMAN_AGENT:
        return True, f"Decision type {decision_type.value} is always human-led"

    return False, "AI decision within parameters"


class DecisionRouter:
    """Routes decisions to the appropriate handler (AI, human, or hybrid)."""

    def __init__(self):
        self.framework = DECISION_FRAMEWORK

    def route(self, decision_type: DecisionType, context: dict) -> dict:
        """Route a decision to the appropriate decision maker.

        Args:
            decision_type: The type of decision
            context: Dict with ai_confidence, deal_size, complexity_score, stage

        Returns:
            Dict with decision_maker, action, escalation_path, rationale
        """
        rule = self.framework.get(decision_type)
        if not rule:
            return {
                "decision_maker": "unknown",
                "action": "escalate",
                "escalation_path": ["ae", "vp"],
                "rationale": f"No decision framework for {decision_type}",
            }

        ai_confidence = context.get("ai_confidence", 0.5)
        deal_size = context.get("deal_size", 0)
        complexity = context.get("complexity_score", 0.5)

        should_esc, esc_reason = should_escalate(decision_type, ai_confidence, deal_size, complexity)

        if should_esc:
            return {
                "decision_maker": "human" if rule.decision_maker == DecisionAgent.HUMAN_AGENT else "hybrid",
                "action": "escalate",
                "escalation_path": rule.escalation_path,
                "rationale": esc_reason,
                "automation_ceiling": rule.automation_ceiling,
            }

        return {
            "decision_maker": "ai_agent",
            "action": "proceed",
            "escalation_path": [],
            "rationale": f"AI can handle {decision_type.value} autonomously",
            "automation_ceiling": rule.automation_ceiling,
        }


def analyze_signal_for_decisions(text: str) -> list[dict]:
    """Analyze a signal and extract decision architecture implications."""
    text_lower = text.lower()
    findings = []

    decision_keywords = {
        DecisionType.PROSPECTING: ["prospect", "target", "icp", "account selection"],
        DecisionType.QUALIFICATION: ["qualify", "disqualify", "lead score", "bant"],
        DecisionType.PRICING: ["pricing", "discount", "quote", "proposal"],
        DecisionType.ESCALATION: ["escalate", "human touch", "executive sponsor"],
        DecisionType.RENEWAL: ["renew", "renewal", "contract", "expand"],
        DecisionType.CHURN: ["churn", "health score", "at risk", "save"],
        DecisionType.TERRITORY: ["territory", "account assignment", "coverage"],
        DecisionType.RESOURCE_ALLOCATION: ["resource", "budget", "headcount", "allocate"],
    }

    for decision_type, keywords in decision_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                rule = DECISION_FRAMEWORK.get(decision_type)
                findings.append({
                    "decision_type": decision_type.value,
                    "matched_keyword": kw,
                    "ai_automation_ceiling": rule.automation_ceiling if rule else None,
                    "decision_maker": rule.decision_maker.value if rule else "unknown",
                    "implication": f"Signal indicates shift in {decision_type.value} decision architecture",
                })
                break

    return findings