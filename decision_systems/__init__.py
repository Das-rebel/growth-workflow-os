"""Decision architecture framework for AI-native organizations.

Exports core decision framework from this module.
Note: escalation.py and decision_analyzer.py require additional classes
(DecisionScope, RiskLevel, LifecycleStage, etc.) not yet in framework.py.
They are companion modules that can be imported directly when needed.

Core exports:
    DecisionType: Enum of decision types in GTM lifecycle
    DecisionAgent: Enum of who can make decisions
    DecisionRule: Dataclass defining decision rules
    DECISION_FRAMEWORK: Dict of decision rules by type
    LifecycleDecision: Decision points in GTM lifecycle
    DecisionRouter: Routes decisions to AI/human/hybrid
    should_escalate: Determine if a decision needs human escalation
    analyze_signal_for_decisions: Extract decision implications from signals
"""

from decision_systems.framework import (
    DecisionType,
    DecisionAgent,
    DecisionRule,
    DECISION_FRAMEWORK,
    LifecycleDecision,
    DecisionRouter,
    should_escalate,
    analyze_signal_for_decisions,
)

__all__ = [
    "DecisionType",
    "DecisionAgent",
    "DecisionRule",
    "DECISION_FRAMEWORK",
    "LifecycleDecision",
    "DecisionRouter",
    "should_escalate",
    "analyze_signal_for_decisions",
]

# --- Companion modules (require additional framework classes) ---
# from decision_systems.escalation import EscalationEngine, EscalationTriggers
# from decision_systems.decision_analyzer import DecisionAnalyzer, DecisionBrief
# These import classes not yet defined in framework.py (DecisionScope, RiskLevel, etc.)
# TODO: align framework.py with what escalation.py and decision_analyzer.py expect