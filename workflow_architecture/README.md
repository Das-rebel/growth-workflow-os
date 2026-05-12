# Workflow Architecture Module

Identifies operational bottlenecks in AI-native organizations and proposes AI-native redesigns. Part of the AI-native Growth Operating System.

---

## Overview

The module analyzes workflow pain points from signals (customer interviews, process observations, metrics) and recommends specific AI-native redesign patterns backed by real operational logic.

**Core problem it solves:** Most AI transformation efforts focus on individual tools, not workflow redesign. The leverage is in redesigning the workflow — not in sprinkling AI onto existing processes.

---

## Architecture

```
workflow_architecture/
├── bottleneck_detector.py   # Rule-based bottleneck classification
├── redesign_patterns.py     # Catalog of 8 AI-native redesign patterns
├── workflow_analyzer.py    # End-to-end analysis pipeline
└── README.md               # This file
```

### `bottleneck_detector.py`

Classifies workflow pain points by **bottleneck type**:

| Type | Description | Automation Potential |
|------|-------------|---------------------|
| `DECISION_LATENCY` | Decisions waiting for human review/approval | Medium (0.55) |
| `COORDINATION_COST` | Cross-functional handoffs introduce delays | Medium-High (0.68) |
| `MANUAL_HANDOFFF` | Human-to-human info transfers without automation | High (0.78) |
| `INFORMATION_ASYMMETRY` | Key actors lack visibility into relevant state | High (0.82) |

**Scoring:**
- `automation_potential`: 0.0-1.0, how automatable this workflow is
- `operational_leverage`: HIGH / MEDIUM / LOW, downstream impact of fixing
- `estimated_fte_savings`: hours/week recovered if automated

**GTM Function mapping:** Maps bottlenecks to Sales, CS, Marketing, Ops, Product, Finance.

**Usage:**
```python
from workflow_architecture import BottleneckDetector

detector = BottleneckDetector()
bottlenecks = detector.analyze(
    "Sales reps spend 3 hours/day manually updating CRM fields from email threads."
)
top = detector.prioritize(bottlenecks, top_n=3)
for b in top:
    print(f"[{b.bottleneck_type.value}] auto={b.automation_potential:.2f} leverage={b.operational_leverage.value}")
```

---

### `redesign_patterns.py`

Catalog of **8 AI-native workflow redesign patterns**, each with:
- `before_state` / `after_state` (detailed markdown descriptions)
- `automation_score` (0.0-1.0)
- `implementation_effort` (low / medium / high)
- `gtm_applicability` (which functions benefit)
- `key_ai_capabilities` required
- `expected_impact` (business outcome)
- `transition_steps` (how to implement)

**The 8 Patterns:**

| Pattern | GTM | Automation | Key Use Case |
|---------|-----|------------|--------------|
| `autonomous_outbound` | Sales, Marketing | 0.85 | Replace manual SDR research + sequencing with AI-driven outbound |
| `ai_cs_triage` | CS, Ops | 0.78 | Auto-classify + route tickets, prioritize by account value |
| `predictive_churn` | CS, Sales | 0.72 | ML models identify at-risk accounts 30-60 days before intent |
| `real_time_lead_scoring` | Sales, Marketing | 0.80 | Dynamic ICP scoring updated with every buyer interaction |
| `dynamic_territory_management` | Sales, Ops | 0.75 | AI-optimized territory assignment that adapts to signals |
| `automated_proposal_generation` | Sales | 0.82 | AI-generated proposals from CRM context in < 2 hours |
| `ai_assisted_negotiation` | Sales | 0.70 | Real-time negotiation intelligence for deal guidance |
| `outcome_based_renewal_automation` | CS, Sales, Finance | 0.76 | Trigger-based renewal from health + outcome signals |

**Access patterns:**
```python
from workflow_architecture import PATTERNS, get_pattern, get_all_patterns

# All patterns
for p in get_all_patterns():
    print(f"{p.name}: {p.automation_score}")

# Filter by GTM function
from workflow_architecture import get_patterns_by_gtm
cs_patterns = get_patterns_by_gtm("customer_success")

# Single pattern detail
pattern = get_pattern("autonomous_outbound")
print(pattern.after_state)
```

---

### `workflow_analyzer.py`

End-to-end analysis pipeline combining the detector + pattern catalog.

**WorkflowAnalysis output includes:**
1. **Detected bottlenecks** — BottleneckSignal list with type, GTM, scores
2. **Recommended patterns** — Top 3-4 patterns matched to detected bottlenecks
3. **Pattern details** — Full before/after state, implementation steps
4. **Automation potential** — Aggregate score 0-1
5. **Priority actions** — Ranked action items
6. **Next steps** — Prescriptive guidance based on analysis

**Integrates with:**
- `BottleneckDetector` — rule-based classification
- `StrategicInferenceEngine` — optional deep inference (when available)
- `RedesignPatterns` — pattern catalog lookup

**Usage:**
```python
from workflow_architecture import WorkflowAnalyzer, quick_analyze

# Full analysis
analyzer = WorkflowAnalyzer(use_deep_inference=True)
result = analyzer.analyze(
    "Our proposal process takes 5 days because legal reviews every version.",
    source="rep_interview",
    category="workflow_pain"
)
print(result.recommended_patterns)
print(result.overall_automation_potential)
print(result.next_steps)

# Quick one-liner
analysis = quick_analyze("Sales reps spend 4 hrs/day on CRM data entry")
```

---

## Integration with Rest of Growth OS

### Signal Collection → Workflow Analysis
Signals collected via `signal_collectors/` flow through to `inference_engines/workflow.py` (WorkflowRedesignEngine). `workflow_analyzer` extends this with rule-based detection + pattern catalog.

### Strategic Memory
Analysis results can be stored in `strategic_memory/` for longitudinal tracking of bottleneck evolution.

### Operating Memos
`WorkflowAnalysis.to_dict()` output can feed into `operating_memos/generator.py` for formal recommendation documents.

---

## Bottleneck Detection Logic

The detector uses **pattern matching + heuristic scoring**:

1. **Regex patterns** match signal language to bottleneck type
2. **GTM function classification** via domain keyword matching
3. **Automation potential** derived from bottleneck type base scores:
   - INFORMATION_ASYMMETRY: 0.82 (AI centralizes and distributes)
   - MANUAL_HANDOFFF: 0.78 (data pipeline automation)
   - COORDINATION_COST: 0.68 (AI orchestration)
   - DECISION_LATENCY: 0.55 (often needs human sign-off)
4. **Penalties** applied for compliance, creative judgment, org culture indicators
5. **Leverage estimation** weights revenue-critical functions (Sales, CS) higher

---

## Example Analysis Output

```python
from workflow_architecture import WorkflowAnalyzer

result = analyzer.analyze(
    "CS managers review every cancellation risk manually. "
    "Churn predictions come two weeks too late. "
    "High-value accounts wait in same queue as everyone else."
)

# result.detected_bottlenecks:
# [BottleneckSignal(bottleneck_type=DECISION_LATENCY, automation_potential=0.68, ...),
#  BottleneckSignal(bottleneck_type=COORDINATION_COST, automation_potential=0.72, ...)]

# result.recommended_patterns:
# ['predictive_churn', 'ai_cs_triage', 'outcome_based_renewal_automation']

# result.overall_automation_potential:
# 0.72
```

---

## Pattern Detail: `autonomous_outbound`

The most impactful pattern for Sales GTM functions:

**Before:** SDRs spend 60% of day on manual research. Emails are static templates with no real-time personalization. Follow-up timing is arbitrary. 12-18 touches over 8-12 weeks for 1 qualified meeting.

**After:** AI scrapes + synthesizes prospect signals within 30 seconds. LLM generates tailored email per prospect using full context. Sequence advances on intent signals within 5 minutes. AI determines optimal send timing per role/industry/persona. Self-correcting sequences: AI monitors engagement by variant and shifts to higher-performing angle.

**Key capabilities required:**
- LLM for personalized copy generation
- Web scraping + data enrichment APIs (Clearbit, Apollo, Clay)
- Intent signal integration (Bombora, BuiltWith)
- CRM writeback automation
- Reinforcement learning on copy A/B variants

**Expected impact:** 3-5x SDR output, 40-80% lift in response rates, 50% reduction in research time per prospect.

---

## Example: Prioritizing Multiple Bottlenecks

```python
from workflow_architecture import BottleneckDetector

detector = BottleneckDetector()
signals = [
    "Sales reps manually update CRM 3 hrs/day",
    "Legal reviews every proposal - 5 day cycle",
    "CS has no visibility into which accounts are at risk until cancellation",
    "Marketing manually builds ABM target lists weekly",
]

all_bottlenecks = []
for sig in signals:
    all_bottlenecks.extend(detector.analyze(sig))

# Prioritize across all signals
top = detector.prioritize(all_bottlenecks, top_n=5)
for b in top:
    print(f"{b.bottleneck_type.value} | {b.gtm_function.value} | "
          f"auto={b.automation_potential:.2f} | leverage={b.operational_leverage.value}")
```

---

## Running Tests

```bash
# Test bottleneck detector
python -m workflow_architecture.bottleneck_detector

# Test pattern catalog
python -m workflow_architecture.redesign_patterns

# Test workflow analyzer
python -m workflow_architecture.workflow_analyzer

# Run full analysis demo
python -c "from workflow_architecture import WorkflowAnalyzer; WorkflowAnalyzer().analyze('Sales reps spend 4 hrs/day on manual CRM updates from email threads')"
```