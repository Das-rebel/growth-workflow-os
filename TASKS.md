# Growth Workflow OS — TASKS.md

---

## Phase 1 — Reposition and rename ✅

- [x] **1.1** Project renamed → `~/growth-workflow-os`
- [x] **1.2** README.md rewritten — tagline, architecture, modules table, business examples, quick start
- [x] **1.3** API migrated — Groq/Mistral working, litellm with Cerebras primary
- [x] **1.4** prompts/system_context.txt — Subhajit Das operator context
- [x] **1.5** Abstract language removed — all docstrings updated to growth-specific

---

## Phase 2 — Ground in business examples ✅

- [x] **2.1** 6 GROWTH_WORKFLOW_EXAMPLES added to `workflow_architecture/redesign_patterns.py`
- [x] **2.2** India fintech org patterns added — `ai_embedded_lending_ops` + `vernacular_ai_growth`
- [x] **2.3** 6-section Growth Workflow Intelligence Brief format
- [x] **2.4** Pipeline runs end-to-end ✅

---

## Phase 3 — Add real signal sources ✅

- [x] **3.1** arXiv collector — `signal_collectors/arxiv_collector.py`, wired into pipeline
- [x] **3.2** Reddit collector — `signal_collectors/reddit_collector.py`, PRAW, graceful failure
- [x] **3.3** All collectors wired into `run_pipeline.py`

---

## Phase 4 — Proof assets ✅

- [x] **4.1** ASCII architecture diagram in README.md
- [x] **4.2** `examples/weekly_memo_example.md` — real output from pipeline
- [x] **4.3** `examples/workflow_redesign_example.md` — crm_segmentation_redesign
- [x] **4.4** `examples/resume_bullet.txt`
- [x] **4.5** `examples/linkedin_carousel.md` — 8-slide outline

---

## Phase 5 — Final verification ✅

**Run:**
```bash
cd ~/growth-workflow-os
export CEREBRAS_API_KEY="csk-2jdpd54822wcdyhv2h3c5h6n4vwk8fj6vrefkfhmh2r552we"
export GROQ_API_KEY="REPLACE_WITH_YOUR_KEY"

python3 tests/test_smoke.py
python3 run_pipeline.py
python3 run_query.py "what growth workflow should I redesign this week?"
```

**Verification summary:**
- ✅ Smoke tests pass
- ✅ 10 org patterns loaded
- ✅ 8 workflow redesign patterns
- ✅ 6 GROWTH_WORKFLOW_EXAMPLES
- ✅ arXiv + RSS collectors wired
- ✅ Reddit collector (needs creds to activate)
- ✅ Weekly brief generates in 6-section format
- ✅ System context loaded into every inference call

**API keys needed for full run:**
- `CEREBRAS_API_KEY` — primary model (cerebras/llama3.1-8b) ✅ working
- `GROQ_API_KEY` — fallback ✅ working
- `REDDIT_CLIENT_ID` + `REDDIT_CLIENT_SECRET` — optional, for Reddit collector
