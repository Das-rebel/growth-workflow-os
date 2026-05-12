# Decision Systems

Decision architecture framework for AI-native organizations. Handles how decisions are made, routed, and executed when AI agents are first-class actors.

## Module Structure

### framework.py — Decision Architecture Core

The foundational concepts:

- **`DecisionScope`** — Four-tier authority scale: AI fully autonomous → AI recommends, human decides → Human needs AI data → Human only
- **`RiskLevel`** — Five-level risk classification (trivial → critical)
- **`LifecycleStage`** — GTM stages: Prospect → Qualify → Close → Renew → Expand
- **`DecisionRightsMatrix`** — Resolves effective scope by combining lifecycle stage, risk, AI confidence, and deal size. Acts as the organizational "constitution" for AI-human boundaries.
- **`DecisionVelocityProfile`** — Time budgets per decision type. Identifies bottlenecks by comparing target vs actual velocity.
- **`DecisionRouter`** — Signal → decision routing rules. Patterns: competitor pricing → repricing decision, usage drop → churn intervention, etc.
- **`LIFECYCLE_DECISION_POINTS`** — 12 canonical gates across the GTM lifecycle (lead scoring, BANT qualification, contract approval, etc.)

### escalation.py — Escalation Engine

Determines when and how to route decisions upward:

- **`EscalationTrigger`** — Six trigger types: low confidence, high risk, deal size exceeded, manual override, policy requirement, timeout
- **`EscalationPath`** — Ordered reviewer chains with SLA windows per stage (e.g., `ai_agent → sales_rep (4h) → team_lead (8h) → vp_sales (24h)`)
- **`EscalationEngine.evaluate()`** — Core method: takes a Decision + context dict, returns `EscalationResult` with should_escalate, urgency, path, and reasons
- **`STANDARD_ESCALATION_PATHS`** — Pre-built paths for sales, CS, legal, product
- **`EscalationTriggers`** — Configurable thresholds for confidence floor (60%), risk ceiling (HIGH), deal size limits ($50k AI max), timeout (24h)

Key insight: escalation is not a failure mode — it's a first-class feature of a healthy AI-native org. The system knows its own limits and routes to the right human at the right time.

### decision_analyzer.py — Signal Analysis

Sits between signal collection and decision execution. Extracts decision implications from signal clusters:

- **`DecisionAnalyzer.analyze_signals()`** — Takes a cluster of signals, returns `DecisionBrief` objects. Handles lifecycle inference, scope resolution, escalation evaluation.
- **`DecisionBrief`** — The output: decision question, options, AI recommendation (if confident enough), context, and escalation metadata
- **`analyze_signal()`** — One-liner convenience function
- **`SIGNAL_DECISION_MAPPING`** — Maps signal category patterns to implied decision types (20+ patterns)

Analysis pipeline: signal cluster → implied decisions → scope resolution → escalation check → decision brief ready for AI or human execution.

## Usage Pattern

```
signals = collect_signals()  # your signal pipeline
analyzer = DecisionAnalyzer()

briefs = analyzer.analyze_signals(signals, lifecycle=Stage.CLOSE, deal_size=75000)
for brief in briefs:
    if brief.escalation_recommended:
        route_to_human(brief)      # send to Slack/email with full brief
        log_escalation(brief)
    elif brief.scope == DecisionScope.AI_FULLY_AUTONOMOUS:
        execute_ai_decision(brief)  # auto-proceed with AI recommendation
    else:
        present_to_human(brief)    # show options, get human decision
        log_human_decision(brief)
```

## Key Configuration Points

1. **`DecisionRightsMatrix`** thresholds — tune confidence floor and deal size limits to match your org's AI trust level
2. **`EscalationTriggers`** — adjust risk ceiling and timeout based on your operational cadence
3. **`STANDARD_ESCALATION_PATHS`** — customize reviewer chains and SLA windows per function
4. **`SIGNAL_DECISION_MAPPING`** — add your domain-specific signal → decision patterns

## Integration

- Uses `signal_collectors.base.Signal` for signal structure
- Uses `inference_engines.base.InferenceEngine` for AI recommendations
- Produces `Decision` objects that flow into `strategic_memory`
- Complements `workflow_architecture` for bottleneck analysis (slow decisions indicate workflow issues)