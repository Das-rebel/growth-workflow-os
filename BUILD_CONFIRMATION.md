# AI-Native Growth Operating System — Build Confirmation

## What Was Built

A strategic intelligence layer for growth organizations that encodes operator judgment into scalable systems. Located at `~/ai-native-growth-os/`.

---

## Architecture

```
signals → interpretation → inference → strategic memory → decision architecture → operating recommendations → organizational redesign
```

### Modules

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `signal_collectors/` | Collect market intelligence from RSS, manual entry | `base.py`, `rss_collector.py`, `manual.py` |
| `inference_engines/` | Generate strategic interpretations via LLM | `base.py`, `strategic.py`, `workflow.py`, `org.py` |
| `strategic_memory/` | Persistent storage (SQLite) for signals, theses, predictions | `store.py` |
| `operating_memos/` | Weekly memo generation engine | `generator.py` |
| `organizational_models/` | 8 AI-native org design patterns | `patterns.py` |
| `decision_systems/` | Decision architecture framework with routing rules | `framework.py`, `escalation.py`, `decision_analyzer.py` |
| `narrative_strategy/` | Positioning analysis and market narrative tracking | `positioning.py`, `market_narrative.py`, `narrative_analyzer.py` |
| `workflow_architecture/` | Bottleneck detection and AI-native redesign patterns | `bottleneck_detector.py`, `redesign_patterns.py`, `workflow_analyzer.py` |

---

## Entry Points

```bash
cd ~/ai-native-growth-os

# Full pipeline: collect → infer → memo
python3 run_pipeline.py

# Weekly memo only
python3 run_weekly.py

# Query memory with natural language
python3 run_query.py "what are the major market shifts?"

# Manual signal entry
python3 -m signal_collectors.manual -t "Stripe launches AI billing agent" -c product_launch

# Smoke tests
python3 tests/test_smoke.py
```

---

## API Configuration

Models routed via `config/settings.yaml`:
- Primary: `groq/llama-3.3-70b-versatile` (fast, free tier)
- Fallback: `mistral/mistral-small-latest`

API keys loaded from `config/.env`:
- `MISTRAL_API_KEY`
- `GROQ_API_KEY`

---

## Strategic Memory

SQLite database at `strategic_memory/growth_os.db` with 3 stores:

| Store | Contents |
|-------|----------|
| `signals` | Market signals with interpretations and strategic weights |
| `theses` | Active strategic beliefs with confidence scores |
| `predictions` | Testable hypotheses with resolution dates |

---

## Organizational Patterns (8 patterns)

1. **Agent-First GTM** — AI agents handle outbound; humans close
2. **AI-Augmented CS** — 70%+ CS automation (QBee pattern)
3. **Full Autonomous Revenue** — Agents own full sales cycle
4. **AI-Hybrid Product** — Product teams with AI agents as members
5. **Hub-and-Spoke Ops** — Central AI ops team, distributed execution
6. **Flat Agent Collective** — Minimal hierarchy, autonomous agents
7. **Human-in-the-Loop Enterprise** — AI amplifies human decisions
8. **Outcome-Based Ops** — Teams defined by outcomes, not functions

---

## Decision Framework (8 decision types)

- PROSPECTING → QUALIFICATION → PRICING → ESCALATION → RENEWAL → CHURN → TERRITORY → RESOURCE_ALLOCATION

`DecisionRouter` routes each decision to AI, human, or hybrid based on:
- AI confidence score
- Deal size threshold
- Complexity score

`should_escalate()` determines when to route from AI to human.

---

## Workflow Redesign Patterns (8 patterns)

1. Autonomous Outbound
2. AI CS Triage
3. Predictive Churn
4. Real-Time Lead Scoring
5. Dynamic Territory Management
6. Automated Proposal Generation
7. AI-Assisted Negotiation
8. Outcome-Based Renewal Automation

---

## Verification Commands

```bash
# Smoke tests
python3 tests/test_smoke.py

# All modules importable
python3 -c "
from organizational_models import ORG_PATTERNS, OrgPatternAnalyzer
from decision_systems import DecisionRouter, DecisionType, should_escalate
from workflow_architecture import WorkflowAnalyzer, get_all_patterns
from narrative_strategy import NarrativeAnalyzer, MarketNarrativeTracker
print('All modules OK')
print(f'Org patterns: {len(ORG_PATTERNS)}')
print(f'Workflow patterns: {len(get_all_patterns())}')
"

# Run pipeline
python3 run_pipeline.py

# Query
python3 run_query.py "what are the top market shifts and recommended actions?"
```

---

## Build Confirmation

- ✅ All 8 modules expanded (not stubs)
- ✅ Full pipeline end-to-end verified (collected signals, inferred, memo generated)
- ✅ Smoke tests pass
- ✅ All modules importable without errors
- ✅ API keys configured in `config/.env`
- ✅ Database populated with seed signals, theses, predictions
- ✅ Weekly memo generated at `operating_memos/output/weekly_memo_2026-05-09.md`
