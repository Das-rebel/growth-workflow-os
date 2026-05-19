# Growth Workflow OS 🧠

**AI-powered strategic operating system for indie hackers and operators.**

Signal collection → Strategic intelligence → Daily execution. Runs on GCP Cloud Run with real-time dashboard.

> "Not just tools. A system that thinks alongside you."

---

## What It Does

```
Your daily operating rhythm:
┌─────────────────────────────────────────────────────────┐
│  Morning (6 AM)                                         │
│    → Signal collectors pull from HN, Twitter, Reddit    │
│    → Strategic thesis updated with new data             │
│    → Top 5 opportunities surfaced for the day           │
├─────────────────────────────────────────────────────────┤
│  Throughout the day                                     │
│    → Alerts fire on high-priority signals                │
│    → Decision memory accumulates                        │
│    → Operating memos generated for key choices           │
├─────────────────────────────────────────────────────────┤
│  Weekly (Sunday)                                        │
│    → Full digest: what happened, what's next            │
│    → Narrative thesis updated                            │
│    → Strategic model refreshed                           │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture

| Component | Purpose | Tech |
|-----------|---------|------|
| [signal_collectors](signal_collectors/) | Pull from HN, Twitter, Reddit, newsletters | Python, GCP |
| [decision_systems](decision_systems/) | Store + retrieve strategic decisions | SQLite + GCS |
| [inference_engines](inference_engines/) | AI synthesis of signals into intelligence | LiteLLM |
| [narrative_strategy](narrative_strategy/) | Thesis + predictions + strategy memo | Python |
| [workflow_architecture](workflow_architecture/) | Pipeline definitions | Python + YAML |
| [app.py](app.py) | Streamlit dashboard (4 pages) | Streamlit |

---

## Quick Start

```bash
# Clone
git clone https://github.com/Das-rebel/growth-workflow-os.git
cd growth-workflow-os

# Install
pip install -r requirements.txt

# Run daily pipeline
python run_daily.py

# Start dashboard
streamlit run app.py
```

**Dashboard:** `fusion-dashboard-338789220059.asia-south1.run.app`

---

## Features

### 📊 Signal Collection
- **HN**: Top stories, comments, ask HN
- **Twitter**: Thread engagements, follower signals
- **Reddit**: Subreddit activity, cross-post trends
- **Email newsletters**: Digest format, auto-tagged

### 🧠 Strategic Intelligence
- **Narrative thesis**: Stores + evolves your market narrative
- **Predictions**: 6-week forward look with confidence scores
- **Operating memos**: Generated for key strategic decisions
- **Decision memory**: All choices logged with outcomes

### 📈 Operations
- **Daily digest**: Every morning, your strategic brief
- **Alert system**: Fires on high-priority signals
- **Weekly digest**: Sunday strategic review
- **Query tool**: Ask anything about your signals

---

## Comparison

| Feature | Growth OS | Notion | Airtable |
|---------|:---------:|:------:|:--------:|
| AI synthesis | ✅ | ❌ | ❌ |
| Signal collection | ✅ | ❌ | ❌ |
| Strategic memory | ✅ | ⚠️ | ⚠️ |
| Daily briefings | ✅ | ❌ | ❌ |
| Alert system | ✅ | ❌ | ❌ |
| Self-improving | ✅ | ❌ | ❌ |

---

## Project Structure

```
growth-workflow-os/
├── signal_collectors/     # Data ingestion
├── decision_systems/      # Memory layer
├── inference_engines/      # AI orchestration
├── narrative_strategy/     # Thesis & predictions
├── workflow_architecture/  # Pipeline definitions
├── operating_memos/        # Generated memos
├── signals/                # Raw signal data
├── strategic_memory/       # Decision history
├── app.py                  # Streamlit dashboard
├── run_daily.py            # Daily pipeline
├── run_weekly.py           # Weekly synthesis
└── requirements.txt
```

---

## Status

**Phase 6 — Daily-Usable System** (May 2026)

| Component | Status |
|-----------|:------:|
| Signal collectors (HN, Twitter, Reddit) | ✅ |
| LiteLLM routing (MiniMax + Mistral) | ✅ |
| Streamlit dashboard v2 (4 pages) | ✅ |
| Signal feed + status bar | ✅ |
| Intelligence page (theses + predictions) | ✅ |
| Progress tracker (parses ROADMAP.md) | ✅ |
| Pipeline runner page | ✅ |
| Daily pipeline (6 AM) | ✅ |
| Weekly digest (Sunday) | ✅ |

---

## Stack

Python 3.11 · Streamlit · LiteLLM · SQLite · GCP Cloud Run · GCS

---

## About

Built for indie hackers and growth operators who need more than a spreadsheet and less than an enterprise BI tool. Tracks signals, learns from decisions, and surfaces intelligence daily.

MIT License
