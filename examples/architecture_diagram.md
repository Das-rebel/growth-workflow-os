# Growth Workflow OS — Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SIGNAL COLLECTORS                             │
│  RSS (a16z, Stratechery, TechCrunch, SaaStr)                     │
│  arXiv (cs.IR+q-fin.GN — fintech, lending, credit, LLM, India)      │
│  Reddit (r/IndiaInvestments, r/fintech, r/IndiaFinance)           │
│  Manual entry (operator observations)                           │
└────────────────────┬──────────────────────────────────────────────┘
                   │  raw signals stored in SQLite
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STRATEGIC INFERENCE ENGINE                          │
│  Groq/Mistral LLM + Subhajit Das operator context               │
│  Prompts/system_context.txt — embedded lending, tier delta,       │
│  credit lifecycle, India fintech mental models                    │
│                                                                  │
│  Output: strategic interpretation + weight + tags               │
└────────────────────┬──────────────────────────────────────────────┘
                   │  interpreted signals + memory
                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│              STRATEGIC MEMORY (SQLite)                           │
│  signals: market signals with interpretations                     │
│  theses:  active strategic beliefs with confidence scores         │
│  predictions: testable hypotheses with resolution dates           │
└────────────────────┬──────────────────────────────────────────────┘
                   │
         ┌─────────┴──────────┐
         ▼                     ▼
┌──────────────────────┐  ┌────────────────────────────────────────┐
│  WEEKLY BRIEF         │  │  ORG + WORKFLOW DECISION ENGINES       │
│  6-section format:    │  │  10 org patterns (incl. India)         │
│  - Signal            │  │  8 workflow redesign patterns           │
│  - What Changed      │  │  6 GROWTH_WORKFLOW_EXAMPLES            │
│  - Workflow to Fix   │  │  8 decision types + routing rules      │
│  - Action           │  │  Narrative positioning tracker          │
│  - Thesis Update    │  │                                      │
│  - Prediction Track  │  │  All grounded in real Subhajit Das     │
└──────────────────────┘  │  metrics (Groww 7x, NIRO, Axis)     │
                          └────────────────────────────────────────┘
```

## Growth Workflow OS

An AI-enabled system that turns market signals into growth workflow redesigns,
operator decisions, and weekly strategic memos.

**Built by Subhajit Das** — IIM Trichy, 10yr fintech growth lead.
