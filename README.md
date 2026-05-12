# Growth Workflow OS

**An AI-enabled system that turns market signals into growth workflow redesigns, operator decisions, and weekly strategic memos. Built by a growth operator, for growth operators.**

---

## What problem does this solve?

Growth teams drown in signals — market shifts, competitor moves, customer behavior, channel changes — but have no system to turn those signals into decisions. Analysis is slow, memory is siloed, and the "right action" lives in someone's head, not a repeatable system.

Growth Workflow OS encodes operator judgment into a pipeline that: collects signals → generates strategic inference → identifies which workflows to redesign → routes decisions → produces a weekly brief.

---

## Architecture

```
SIGNAL COLLECTORS          INFERENCE ENGINE           MEMORY
RSS / arXiv / Reddit  →  Groq/Mistral LLM    →  SQLite
Manual entry              + operator context        signals
                           (Subhajit Das)
                                                theses
                                                predictions
                              ↓
              ┌─────────────────────────────────────────┐
              │  GROWTH WORKFLOW INTELLIGENCE BRIEF    │
              │  6-section weekly format               │
              │  POV · Changes · Workflow · Action      │
              └─────────────────────────────────────────┘

              ORG + WORKFLOW DECISION ENGINES
              10 org patterns (incl. India fintech)
              8 workflow redesign patterns
              6 GROWTH_WORKFLOW_EXAMPLES
```

---

## Modules

| Module | What growth workflow it improves |
|--------|--------------------------------|
| `signal_collectors/` | RSS + arXiv feed → weekly signal store |
| `inference_engines/` | Turn raw signals into strategic interpretations |
| `strategic_memory/` | SQLite layer: signals, theses, predictions persist |
| `operating_memos/` | Weekly Growth Intelligence Brief (5-section format) |
| `organizational_models/` | 10 org design patterns for AI-native growth teams |
| `decision_systems/` | 8 decision types with AI/human routing rules |
| `narrative_strategy/` | Positioning analysis + market narrative tracking |
| `workflow_architecture/` | 8 workflow redesign patterns with before/after |

---

## Business examples built in

Based on real Subhajit Das metrics:

1. **CRM Segmentation Redesign** — "Weekly manual CRM cohort review → AI-assisted next-action routing" (Groww: 80% DAU improvement)
2. **Retention Escalation** — "At-risk user detection → tiered intervention → human escalation" (Groww: 60% revenue boost)
3. **Lead Qualification Routing** — "Inbound lead → AI qualification → human/AI routing" (NIRO: 50% onboarding reduction)
4. **Campaign Prioritisation** — "Weekly planning → AI-ranked budget allocation" (Axis Bank: ₹1500Cr secured loan growth)
5. **Embedded Lending Activation** — "New D2C partner → eligibility → KYC → activation" (NIRO: ₹70Cr/month disbursals)
6. **Lifecycle Automation** — "Lifecycle event → trigger → workflow → operator memo" (Groww: LTV-focused growth)

---

## Quick start

```bash
# Clone and enter
cd ~/growth-workflow-os

# Install dependencies
pip install -r requirements.txt

# Add your API key
cp config/.env.example config/.env
# Add ANTHROPIC_API_KEY to config/.env

# Run full pipeline
python3 run_pipeline.py

# Weekly brief only
python3 run_weekly.py

# Query memory
python3 run_query.py "what workflow should I redesign this week?"

# Manual signal entry
python3 -m signal_collectors.manual -t "Cred launches new BNPL product" -c product_launch
```

---

## What you get every week

A **Growth Intelligence Brief** — a 5-section memo:
1. **This Week's POV** — One opinionated take on the most important signal in Subhajit's voice
2. **Content Angles** — 3 content hooks with format/arc/audience for LinkedIn or podcast
3. **Resume Delta** — Keywords to add or deprioritise based on market shifts
4. **Competitor Signal** — What a competitor did + what it means for you
5. **Paper to Reference** — Relevant arXiv paper + 1-line relevance

Each brief reads like a growth operator wrote it — specific metrics, India context, falsifiable claims. Not generic AI summarization.

---

## Tech stack

- **Models**: Anthropic Claude Sonnet 4 (primary) via LiteLLM, Groq/Mistral fallback
- **Memory**: SQLite (signals, theses, predictions)
- **Signal sources**: RSS feeds, arXiv, manual entry
- **Orchestration**: Python, Click CLI, Rich terminal output

---

## Documentation

- `CLAUDE.md` — System identity and positioning for AI agents
- `BUILD_CONFIRMATION.md` — What was built and how to verify
