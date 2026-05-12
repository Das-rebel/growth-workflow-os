# Growth Workflow OS — Roadmap & Progress

## Goal
Ship Growth OS as a daily-usable strategic operating layer with web dashboard + richer signals.

---

## Phase 6 — Daily-Usable System

### P0 — Blocking Fixes

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 6.1 | Fix model routing → MiniMax primary, Mistral fallback | None | AI | ✅ |
| 6.2 | Remove all Anthropic/Groq/Cerebras references | None | AI | ✅ |
| 6.3 | Fix LiteLLM warnings (env vars + null handlers) | None | AI | ✅ |

### P1 — Dashboard

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 6.4 | Build Streamlit app v2 (4 pages) | 6.1 | AI | ✅ |
| 6.5 | Signal feed with collector status bar | 6.4 | AI | ✅ |
| 6.6 | Intelligence page (theses + predictions + memo) | 6.4 | AI | ✅ |
| 6.7 | Progress tracker page (parses ROADMAP.md) | 6.4 | AI | ✅ |
| 6.8 | Pipeline runner page with data health | 6.4 | AI | ✅ |

### P2 — Signal Sources

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 6.9 | Hacker News collector (Algolia API) | None | AI | ✅ |
| 6.10 | ProductHunt collector (RSS) | None | AI | ✅ |
| 6.11 | Google Trends collector (RSS) | None | AI | ✅ |
| 6.12 | Twitter/X collector (Nitter) | None | AI | ✅ |
| 6.13 | LinkedIn collector (experimental) | None | AI | ✅ |
| 6.14 | Wire all collectors into pipeline | 6.9-6.13 | AI | ✅ |

### P3 — Reddit Integration

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 6.15 | Extract cookies from Brave browser | None | AI | ✅ |
| 6.16 | Fix Reddit collector dotenv path | None | AI | ✅ |
| 6.17 | Set REDDIT_USER=Daslearnsai | None | AI | ✅ |

### P4 — Automation & Alerts

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 6.18 | Daily signal collection cron (run_daily.py + launchd) | None | AI | ✅ |
| 6.19 | WhatsApp alerts for high-priority signals (run_alerts.py) | 6.18 | AI | ✅ ⚠️ |
| 6.20 | Daily digest memo (run_digest.py) | 6.18 | AI | ✅ |
| 6.21 | Competitor monitoring (competitor_collector.py, 9 companies) | None | AI | ✅ |

---

## Phase 7 — Ship Publicly

| # | Task | Dependency | Owner | Status |
|---|------|-----------|-------|--------|
| 7.1 | GitHub repo cleanup (remove hardcoded keys) | None | Human | ❌ |
| 7.2 | GitHub Actions CI (smoke tests) | None | AI | ❌ |
| 7.3 | Deploy dashboard (Streamlit Cloud or Railway) | 6.8 | AI | ❌ |
| 7.4 | Write LinkedIn carousel content | 7.3 | Human | ❌ |
| 7.5 | Record demo video / Loom walkthrough | 7.3 | Human | ❌ |
| 7.6 | Add to resume as portfolio project | 7.3 | Human | ❌ |

---

## Dependency Graph

```
6.1 (MiniMax routing) ✅
6.4 (Dashboard v2) ✅
6.9-6.13 (Signal sources) ✅
6.15-6.17 (Reddit cookies) ✅
       │
       ▼
6.18 (Cron) ──▶ 6.19 (Alerts)
            ──▶ 6.20 (Daily digest)
            ──▶ 6.21 (Competitor tracking)
       │
       ▼
7.1-7.6 (Ship publicly)
```

## What's next
1. **6.18** — Set up cron for daily runs
2. **6.21** — Add competitor monitoring
3. **7.1** — Clean up repo for public
