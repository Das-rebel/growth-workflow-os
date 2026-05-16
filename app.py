#!/usr/bin/env python3
"""Growth Workflow OS — Dashboard v3
OpenUI-inspired dark theme · Fusion task tracker · Signal intelligence."""

import os, sys, json, sqlite3, subprocess
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

try:
    from config import load_env
    load_env()
except ImportError:
    pass

DB_PATH = os.getenv("GROWTH_OS_DB_PATH") or str(ROOT / "strategic_memory" / "growth_os.db")
MEMO_DIR = ROOT / "operating_memos" / "output"
ROADMAP_FILE = ROOT / "ROADMAP.md"
FUSION_DB = Path.home() / ".fusion" / "fusion.db"

st.set_page_config(page_title="Growth OS", page_icon="🧠", layout="wide", initial_sidebar_state="collapsed")

# ─── Dark theme CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --bg: #0f1117;
    --surface: #161922;
    --card: #1c1f2e;
    --border: #2a2d3e;
    --text: #e2e4f0;
    --muted: #6b7094;
    --accent: #6366f1;
    --accent2: #8b5cf6;
    --green: #22c55e;
    --yellow: #eab308;
    --red: #ef4444;
    --orange: #f97316;
}
* { box-sizing: border-box; }
.stApp { background: var(--bg) !important; color: var(--text) !important; }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }
[data-testid="stMainBlockContainer"] { background: var(--bg); padding: 1.5rem 2rem; }
h1, h2, h3, h4 { color: var(--text) !important; font-weight: 600 !important; }
.stMetric { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; padding: 16px 20px !important; }
.stMetricValue { color: var(--accent) !important; font-size: 1.6rem !important; font-weight: 700 !important; }
.stMetricLabel { color: var(--muted) !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.05em; }
.stExpander { background: var(--card) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
.stTabs [data-baseweb="tab-list"] { background: var(--surface); border-radius: 8px; gap: 4px; padding: 4px; }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; border-radius: 6px; padding: 8px 16px; font-weight: 500; }
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: white !important; }
.stButton>button { background: var(--accent); color: white; border: none; border-radius: 8px; padding: 0.5rem 1.5rem; font-weight: 600; }
.stButton>button:hover { background: #4f52d4; }
.stTextInput>div>div>input, .stSelectbox>div>div>div { background: var(--card) !important; border: 1px solid var(--border) !important; color: var(--text) !important; border-radius: 8px; }
.stNumberInput>div>div>input { background: var(--card) !important; border: 1px solid var(--border) !important; color: var(--text) !important; }
hr { border-color: var(--border) !important; }
.code-block { background: #0d1117; border: 1px solid var(--border); border-radius: 8px; padding: 16px; font-family: 'Courier New', monospace; font-size: 0.8rem; color: #c9d1d9; white-space: pre-wrap; }
.kpi-card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; text-align: center; }
.kpi-value { font-size: 2rem; font-weight: 700; color: var(--accent); }
.kpi-label { font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 4px; }
.fusion-column { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 12px; min-height: 300px; }
.fusion-col-header { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); padding: 8px 4px; border-bottom: 1px solid var(--border); margin-bottom: 8px; }
.fusion-task { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; cursor: pointer; transition: border-color 0.2s; }
.fusion-task:hover { border-color: var(--accent); }
.fusion-task-id { font-size: 0.7rem; color: var(--muted); font-family: monospace; }
.fusion-task-title { font-size: 0.85rem; font-weight: 500; color: var(--text); margin: 4px 0; }
.priority-high { border-left: 3px solid var(--red); }
.priority-medium { border-left: 3px solid var(--yellow); }
.priority-normal { border-left: 3px solid var(--accent); }
.badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.7rem; font-weight: 600; }
.badge-done { background: rgba(34,197,94,0.15); color: var(--green); }
.badge-progress { background: rgba(99,102,241,0.15); color: var(--accent); }
.badge-todo { background: rgba(107,112,148,0.15); color: var(--muted); }
.badge-triage { background: rgba(249,115,22,0.15); color: var(--orange); }
.instructions { background: linear-gradient(135deg, rgba(99,102,241,0.1), rgba(139,92,246,0.05)); border: 1px solid rgba(99,102,241,0.3); border-radius: 12px; padding: 20px; }
.instructions h4 { color: var(--accent) !important; margin-top: 0; }
.phase-header { background: var(--surface); border-radius: 8px; padding: 8px 16px; margin: 16px 0 8px; font-weight: 600; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); }
</style>
""", unsafe_allow_html=True)


# ─── DB helpers ──────────────────────────────────────────────────────────
def get_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn

def query(sql, params=(), db=DB_PATH):
    with get_db(db) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def fusion_query(sql, params=()):
    if not FUSION_DB.exists():
        return []
    try:
        with get_db(str(FUSION_DB)) as conn:
            return [dict(r) for r in conn.execute(sql, params).fetchall()]
    except Exception:
        return []


# ─── ROADMAP parser ──────────────────────────────────────────────────────
def parse_roadmap():
    if not ROADMAP_FILE.exists():
        return []
    content = ROADMAP_FILE.read_text()
    tasks, phase = [], ""
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("## Phase") or (line.startswith("###") and "Phase" in line):
            phase = line.lstrip("#").strip()
        if line.startswith("|") and "---" not in line and not line.startswith("| #"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if len(cells) >= 5 and cells[0] and not cells[0].startswith("#") and not cells[0][0].isdigit() is False:
                try:
                    status = "✅" if "✅" in cells[4] else ("🔄" if "🔄" in cells[4] else ("❌" if "❌" in cells[4] else "⬜"))
                    owner = cells[3] if len(cells) > 3 else "AI"
                    tasks.append({"id": cells[0], "title": cells[1], "dep": cells[2] if len(cells) > 2 else "", "owner": owner, "status": status, "phase": phase})
                except (IndexError, ValueError):
                    pass
    return tasks


# ─── Fusion tasks ────────────────────────────────────────────────────────
def get_fusion_tasks():
    """Read Fusion tasks from the cloud dashboard API (source of truth)."""
    import urllib.request, json

    CLOUD_API = "https://fusion-dashboard-338789220059.asia-south1.run.app/api/tasks"
    BEARER_TOKEN = "fn_68fc5898c901a22af5fb52576b0dbf6e"

    try:
        req = urllib.request.Request(
            CLOUD_API,
            headers={
                "Authorization": f"Bearer {BEARER_TOKEN}",
                "Accept": "application/json"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            tasks = json.loads(resp.read())
    except Exception:
        return {"triage": [], "todo": [], "in-progress": [], "done": []}

    if not isinstance(tasks, list):
        return {"triage": [], "todo": [], "in-progress": [], "done": []}

    cols = {"triage": [], "todo": [], "in-progress": [], "done": []}
    for t in tasks:
        col = (t.get("column") or "triage").lower().strip()
        col = {
            "in_progress": "in-progress",
            "in-progress": "in-progress",
            "done": "done",
            "triage": "triage",
            "todo": "todo",
            "backlog": "todo",
        }.get(col, "triage")

        title = t.get("title") or "Untitled"
        desc = t.get("description") or ""
        # Strip markdown from description for cleaner display
        if desc.startswith("##"):
            desc = "\n".join(desc.split("\n")[2:]).strip()[:200]

        cols.setdefault(col, []).append({
            "id": t.get("id", ""),
            "title": title[:80],
            "desc": desc[:200],
            "priority": t.get("priority", "normal"),
            "status": t.get("status") or "",
        })

    return cols


def sidebar():
    with st.sidebar:
        st.markdown("# 🧠 Growth OS")
        st.markdown("---")
        page = st.radio("Navigate", ["📡 Signals", "🧠 Intelligence", "🚀 Progress", "⚡ Pipeline"], label_visibility="collapsed")
        st.markdown("---")

        # Live stats
        try:
            with get_db() as conn:
                sig = conn.execute("SELECT COUNT(*) FROM signals").fetchone()[0]
                thes = conn.execute("SELECT COUNT(*) FROM theses WHERE invalidated_at IS NULL").fetchone()[0]
                pred = conn.execute("SELECT COUNT(*) FROM predictions WHERE outcome IS NULL").fetchone()[0]
                latest = conn.execute("SELECT MAX(collected_at) FROM signals").fetchone()[0] or ""
        except:
            sig = thes = pred = 0
            latest = ""

        for label, val in [("Signals", f"{sig:,}"), ("Active Theses", thes), ("Pending Preds", pred)]:
            st.markdown(f"<div class='kpi-card'><div class='kpi-value' style='font-size:1.4rem'>{val}</div><div class='kpi-label'>{label}</div></div>", unsafe_allow_html=True)

        if latest:
            st.caption(f"Last signal: {str(latest)[:16]}")

        st.markdown("---")
        st.markdown("### 🔗 Links")
        st.markdown("- [📊 Dashboard](http://localhost:8501)")
        st.markdown("- [🚀 Fusion Board](http://localhost:4040)")
        st.markdown("- [📝 ROADMAP.md](https://github.com/Das-rebel/growth-workflow-os)")
        st.markdown("---")
        st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

        if st.button("🔄 Refresh"):
            st.rerun()
        return page


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — SIGNALS
# ═══════════════════════════════════════════════════════════════════════════
def page_signals():
    st.header("📡 Signal Feed")

    # Collector status
    collectors = ["RSS", "Reddit", "arXiv", "HackerNews", "ProductHunt", "Google Trends", "Twitter", "LinkedIn", "Competitor"]
    src_map = {"RSS": "rss", "Reddit": "reddit", "arXiv": "arxiv", "HackerNews": "hackernews", "ProductHunt": "producthunt", "Google Trends": "google_trends", "Twitter": "twitter", "LinkedIn": "linkedin", "Competitor": "competitor"}
    cols = st.columns(len(collectors))
    for i, name in enumerate(collectors):
        src = src_map[name]
        row = query(f"SELECT COUNT(*) as c FROM signals WHERE source LIKE '%' || ? || '%'", (src,))
        n = row[0]["c"] if row else 0
        cols[i].metric(f"{'✅' if n > 0 else '⚪'} {name}", f"{n}")

    st.markdown("---")

    # Filters
    c1, c2, c3, c4 = st.columns([2, 2, 1, 2])
    with c1:
        src_f = st.selectbox("Source", ["All"] + [r["source"] for r in query("SELECT DISTINCT source FROM signals ORDER BY source")])
    with c2:
        cat_f = st.selectbox("Category", ["All"] + [r["category"] for r in query("SELECT DISTINCT category FROM signals ORDER BY category")])
    with c3:
        days = st.selectbox("Days", [1, 7, 14, 30, 90, 365], index=1)
    with c4:
        search = st.text_input("🔍 Search", placeholder="keyword...")

    where = ["collected_at > datetime('now', ?)"]
    params = [f"-{days} days"]
    if src_f != "All":
        where.append("source = ?"); params.append(src_f)
    if cat_f != "All":
        where.append("category = ?"); params.append(cat_f)
    if search:
        where.append("(text LIKE ? OR source LIKE ?)"); params.extend([f"%{search}%", f"%{search}%"])
    wheresql = " AND ".join(where)

    # Chart
    chart_data = query(f"SELECT date(collected_at) as day, source, COUNT(*) as cnt FROM signals WHERE {wheresql} GROUP BY day, source ORDER BY day", tuple(params))
    if chart_data:
        fig = px.area(chart_data, x="day", y="cnt", color="source", title="Signals Over Time", color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(template="plotly_dark", height=280, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02))
        st.plotly_chart(fig, width="stretch")

    st.markdown("---")

    # Signal cards
    total = query(f"SELECT COUNT(*) as c FROM signals WHERE {wheresql}", tuple(params))[0]["c"]
    pg = st.number_input("Page", 1, max(1, -(-total // 25)), value=1)
    signals = query(f"SELECT id, text, source, category, url, collected_at, interpretation, strategic_weight FROM signals WHERE {wheresql} ORDER BY collected_at DESC LIMIT 25 OFFSET ?", tuple(params) + ((pg-1)*25,))

    for s in signals:
        w = s["strategic_weight"]
        w_str = f"{'🟢' if w and w>=0.7 else '🟡' if w and w>=0.4 else '🔴'} `{w:.2f}`" if w else ""
        with st.expander(f"**{s['source']}** {w_str} · {s['text'][:90]}{'...' if len(s['text'])>90 else ''}"):
            st.markdown(s["text"])
            if s["url"]:
                st.markdown(f"🔗 [Link]({s['url']})")
            if s["interpretation"]:
                st.markdown(f"**Interpretation:** {s['interpretation'][:400]}")
            cols2 = st.columns(3)
            cols2[0].caption(f"#{s['id']} · {s['category']}")
            cols2[1].caption(f"⏰ {s['collected_at'][:16]}")

    st.caption(f"Page {pg} · {total} total signals")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════
def page_intelligence():
    st.header("🧠 Intelligence")
    tab1, tab2, tab3 = st.tabs(["💡 Theses", "🔮 Predictions", "📝 Weekly Memo"])

    with tab1:
        theses = query("SELECT * FROM theses ORDER BY created_at DESC")
        active = [t for t in theses if not t.get("invalidated_at")]
        invalid = [t for t in theses if t.get("invalidated_at")]
        c1, c2, c3 = st.columns(3)
        c1.metric("Active", len(active))
        c2.metric("Invalidated", len(invalid))
        c3.metric("Total", len(theses))
        for t in active[:20]:
            conf = t.get("confidence", 0.5) or 0.5
            icon = "🟢" if conf >= 0.8 else ("🟡" if conf >= 0.6 else "🔴")
            st.markdown(f"{icon} **[{t.get('thesis_type','belief')}]** {t['thesis_text']}")
            st.caption(f"confidence: {conf:.1f} · {t['created_at'][:10]}")
            st.divider()
        if invalid:
            with st.expander(f"⚠️ Invalidated ({len(invalid)})"):
                for t in invalid:
                    st.markdown(f"~~{t['thesis_text']}~~")
                    st.caption(f"invalidated: {t['invalidated_at'][:10]}")

    with tab2:
        preds = query("SELECT * FROM predictions ORDER BY created_at DESC")
        pending = [p for p in preds if not p.get("outcome")]
        resolved = [p for p in preds if p.get("outcome")]
        c1, c2 = st.columns(2)
        c1.metric("Pending", len(pending))
        c2.metric("Resolved", len(resolved))
        for p in pending[:20]:
            st.markdown(f"⏳ {p['prediction_text']}")
            st.caption(f"resolve by: {p.get('resolve_by','—')} · {p['created_at'][:10]}")
            st.divider()
        if resolved:
            with st.expander(f"Resolved ({len(resolved)})"):
                for p in resolved:
                    icon = "✅" if p.get("outcome_correct") == "true" else "❌"
                    st.markdown(f"{icon} {p['prediction_text']}")
                    st.caption(f"outcome: {p.get('outcome','—')}")

    with tab3:
        memos = sorted(MEMO_DIR.glob("weekly_memo_*.md"), reverse=True)
        if not memos:
            st.warning("No memos yet. Run the pipeline first.")
            return
        opts = [f.name.replace("weekly_memo_", "").replace(".md", "") for f in memos]
        sel = st.selectbox("Memo", opts)
        path = MEMO_DIR / f"weekly_memo_{sel}.md"
        content = path.read_text()
        st.markdown(content)
        st.download_button("Download", content, path.name, "text/markdown")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 3 — PROGRESS (FUSION + ROADMAP)
# ═══════════════════════════════════════════════════════════════════════════
def page_progress():
    st.header("🚀 Progress Tracker")

    # ── Instructions panel ──
    with st.expander("📋 Growth OS Setup — Click to expand", expanded=True):
        st.markdown("""
        <div class="instructions">
        <h4>🚀 Growth OS Project — Active in Fusion</h4>

        <b>✅ Fusion Project Created:</b> <code>GrowthOS</code> — registered at <code>http://localhost:4040</code><br>
        <br>

        <b>📋 Current Tasks in Fusion (FN-009 to FN-015):</b><br>
        <table style='font-size:0.85rem'>
        <tr><td><b>ID</b></td><td><b>Task</b></td><td><b>Priority</b></td></tr>
        <tr><td>FN-009</td><td>Set up Growth OS Telegram alerts</td><td>high</td></tr>
        <tr><td>FN-010</td><td>Add /growthos command to OmniClaw server.js</td><td>normal</td></tr>
        <tr><td>FN-011</td><td>Build Telegram polling alert agent</td><td>normal</td></tr>
        <tr><td>FN-012</td><td>Fix dashboard dark theme CSS</td><td>normal</td></tr>
        <tr><td>FN-013</td><td>Wire competitor_collector into run_daily.py</td><td>normal</td></tr>
        <tr><td>FN-014</td><td>Deploy dashboard to Streamlit Cloud</td><td>normal</td></tr>
        <tr><td>FN-015</td><td>Write LinkedIn carousel content</td><td>normal</td></tr>
        </table>
        <br>

        <b>Step 1: Open Fusion</b><br>
        <a href="http://localhost:4040/?token=fn_68fc5898c901a22af5fb52576b0dbf6e">http://localhost:4040</a><br>
        Select project <code>GrowthOS</code>, then create and run tasks:<br>
        <code>/fusion task create "Your task name"</code><br>
        <code>/fusion task run &lt;id&gt;</code><br>
        <br>

        <b>Step 2: Telegram Alerts</b><br>
        1. Open Telegram → send any message to <code>@Dasomni_bot</code><br>
        2. This registers your chat ID for alerts<br>
        <br>

        <b>Step 3: Daily Cron (6 AM IST — active)</b><br>
        Verify: <code>crontab -l</code><br>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Two columns: Fusion left, ROADMAP right ──
    col_fusion, col_roadmap = st.columns([1, 1])

    with col_fusion:
        st.markdown("### 🤖 Fusion Task Tracker")
        st.caption("AI-powered task executor — tasks run in isolated git worktrees")

        fusion_tasks = get_fusion_tasks()
        fusion_cols = ["triage", "todo", "in-progress", "done"]
        fusion_labels = {"triage": "🔴 Triage", "todo": "📋 Todo", "in-progress": "🔄 In Progress", "done": "✅ Done"}

        # Show as kanban columns
        kcols = st.columns(len(fusion_cols))
        for i, col_name in enumerate(fusion_cols):
            items = fusion_tasks.get(col_name, [])
            with kcols[i]:
                st.markdown(f"<div class='fusion-col-header'>{fusion_labels[col_name]} ({len(items)})</div>", unsafe_allow_html=True)
                if not items:
                    st.caption("No tasks")
                for item in items:
                    pri_class = f"priority-{item['priority']}" if item['priority'] != 'normal' else ""
                    st.markdown(f"<div class='fusion-task {pri_class}'><div class='fusion-task-id'>{item['id']}</div><div class='fusion-task-title'>{item['title']}</div></div>", unsafe_allow_html=True)

        if not any(fusion_tasks.values()):
            st.info("No Fusion tasks yet. Configure Fusion above to start tracking tasks.")

        st.markdown("---")
        st.markdown("**Open Fusion:** [http://localhost:4040](http://localhost:4040/?token=fn_68fc5898c901a22af5fb52576b0dbf6e)")

    with col_roadmap:
        st.markdown("### 📋 ROADMAP.md Tasks")
        st.caption("Project tasks parsed from ROADMAP.md — checkboxes persist")

        roadmap_tasks = parse_roadmap()
        if not roadmap_tasks:
            st.info("No tasks in ROADMAP.md")
        else:
            # Group by phase
            phases = {}
            for t in roadmap_tasks:
                phases.setdefault(t.get("phase", "Other"), []).append(t)

            for phase, ptasks in phases.items():
                st.markdown(f"<div class='phase-header'>📦 {phase}</div>", unsafe_allow_html=True)
                for t in ptasks:
                    badge = f"<span class='badge badge-done'>✅ Done</span>" if t["status"] == "✅" else (
                        f"<span class='badge badge-progress'>🔄 In Progress</span>" if t["status"] == "🔄" else
                        f"<span class='badge badge-todo'>⬜ Todo</span>")
                    st.markdown(f"{badge} **{t['id']}** — {t['title']} <span style='color:var(--muted)'>· {t.get('owner','AI')}</span>")

            st.markdown("---")
            # Add task form
            with st.expander("➕ Add Task to ROADMAP"):
                with st.form("add_task"):
                    tid = st.text_input("Task ID", placeholder="e.g. 7.2")
                    title = st.text_input("Title")
                    phase = st.selectbox("Phase", ["Phase 6", "Phase 7", "Phase 8"])
                    owner = st.selectbox("Owner", ["AI", "Human"])
                    if st.form_submit_button("Add"):
                        st.info(f"Task {tid}: {title} added to {phase}. Edit ROADMAP.md manually to persist.")


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 4 — PIPELINE
# ═══════════════════════════════════════════════════════════════════════════
def page_pipeline():
    st.header("⚡ Pipeline")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### ▶️ Full Pipeline")
        st.caption("Collect → Interpret → Infer → Memo")
        if st.button("Run Full Pipeline", type="primary", use_container_width=True):
            with st.spinner("Running..."):
                r = subprocess.run([sys.executable, str(ROOT/"run_pipeline.py")], capture_output=True, text=True, timeout=600)
                if r.returncode == 0:
                    st.success("✅ Pipeline complete!")
                    st.code(r.stdout[-3000:], language="bash")
                else:
                    st.error(f"❌ Failed ({r.returncode})")
                    st.code(r.stderr[-1000:], language="bash")
    with c2:
        st.markdown("#### 📡 Signals Only")
        st.caption("Collect signals without inference")
        if st.button("Collect Signals", use_container_width=True):
            with st.spinner("Collecting..."):
                r = subprocess.run([sys.executable, str(ROOT/"run_daily.py")], capture_output=True, text=True, timeout=120)
                if r.returncode == 0:
                    st.success("✅ Collected!")
                    st.code(r.stdout[-2000:], language="bash")
                else:
                    st.error(f"❌ {r.returncode}")
    with c3:
        st.markdown("#### 📝 Memo Only")
        st.caption("Generate memo from existing signals")
        if st.button("Generate Memo", use_container_width=True):
            with st.spinner("Generating..."):
                r = subprocess.run([sys.executable, str(ROOT/"run_digest.py")], capture_output=True, text=True, timeout=120)
                if r.returncode == 0:
                    st.success("✅ Digest generated!")
                    st.code(r.stdout[-2000:], language="bash")
                else:
                    st.error(f"❌ {r.returncode}")

    st.markdown("---")

    # Data health
    st.subheader("📊 Data Health")
    try:
        health = query("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT source) as sources,
                MIN(collected_at) as earliest,
                MAX(collected_at) as latest,
                COUNT(CASE WHEN interpretation IS NOT NULL THEN 1 END) as interpreted
            FROM signals
        """)[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Signals", f"{health['total']:,}")
        c2.metric("Sources", health["sources"])
        c3.metric("Interpreted", f"{health['interpreted']} ({100*health['interpreted']//max(health['total'],1)}%)")
        c4.metric("Range", f"{str(health['earliest'])[:10]} → {str(health['latest'])[:10]}")
    except Exception as e:
        st.warning(f"Could not load health: {e}")

    # Source breakdown
    src_data = query("SELECT source, COUNT(*) as cnt FROM signals GROUP BY source ORDER BY cnt DESC")
    if src_data:
        fig = px.bar(src_data, x="source", y="cnt", title="Signals by Source", color="cnt", color_continuous_scale="Viridis")
        fig.update_layout(template="plotly_dark", height=300, xaxis_tickangle=-30)
        st.plotly_chart(fig, width="stretch")

    # Model config
    st.subheader("🧠 Model Config")
    try:
        from config import load_settings
        settings = load_settings()
        for purpose, cfg in settings.get("models", {}).items():
            st.markdown(f"- **{purpose}**: `{cfg.get('model', '?')}` → `{cfg.get('fallback', '?')}`")
    except Exception:
        st.info("Could not load settings")


# ─── Main ────────────────────────────────────────────────────────────────
def main():
    page = sidebar()
    pages = {
        "📡 Signals": page_signals,
        "🧠 Intelligence": page_intelligence,
        "🚀 Progress": page_progress,
        "⚡ Pipeline": page_pipeline,
    }
    fn = pages.get(page)
    if fn:
        fn()
    else:
        st.error(f"Unknown page: {page}")

if __name__ == "__main__":
    main()
