#!/usr/bin/env python3
"""Growth OS Content Drafts API — serves drafts to OmniClaw Telegram bot.

GET /api/drafts         → list all drafts (JSON)
GET /api/drafts/<id>    → single draft
POST /api/drafts/<id>/approve → mark approved
POST /api/drafts/<id>/reject  → mark rejected
"""

import os, sys, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Load env
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / "config" / ".env")

DB_PATH = os.getenv("GROWTH_OS_DB_PATH") or str(ROOT / "strategic_memory" / "growth_os.db")
PORT = int(os.getenv("PORT", 8080))

from flask import Flask, jsonify, request

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/drafts", methods=["GET"])
def list_drafts():
    """List all drafts, optionally filtered by status/platform."""
    status = request.args.get("status")
    platform = request.args.get("platform")
    limit = int(request.args.get("limit", 20))

    conn = get_db()
    conn.row_factory = sqlite3.Row

    sql = "SELECT * FROM content_drafts WHERE 1=1"
    params = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if platform:
        sql += " AND platform = ?"
        params.append(platform)
    sql += " ORDER BY generated_at DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(sql, params).fetchall()
    conn.close()

    drafts = []
    for r in rows:
        d = dict(r)
        d["generated_at"] = r["generated_at"]
        d["reviewed_at"] = r["reviewed_at"] or None
        d["approved_at"] = r["approved_at"] or None
        d["posted_at"] = r["posted_at"] or None
        d["signal_sources"] = json.loads(r["signal_sources"]) if r["signal_sources"] else []
        d["vault_context"] = json.loads(r["vault_context"]) if r["vault_context"] else {}
        drafts.append(d)

    return jsonify(drafts)


@app.route("/api/drafts/<int:draft_id>", methods=["GET"])
def get_draft(draft_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM content_drafts WHERE id = ?", (draft_id,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    d = dict(row)
    d["signal_sources"] = json.loads(row["signal_sources"]) if row["signal_sources"] else []
    d["vault_context"] = json.loads(row["vault_context"]) if row["vault_context"] else {}
    return jsonify(d)


@app.route("/api/drafts/<int:draft_id>/approve", methods=["POST"])
def approve_draft(draft_id):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE content_drafts SET status = ?, approved_at = ? WHERE id = ?",
                 ("approved", now, draft_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "draft_id": draft_id, "status": "approved"})


@app.route("/api/drafts/<int:draft_id>/reject", methods=["POST"])
def reject_draft(draft_id):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE content_drafts SET status = ?, reviewed_at = ? WHERE id = ?",
                 ("rejected", now, draft_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "draft_id": draft_id, "status": "rejected"})


@app.route("/api/drafts/<int:draft_id>/posted", methods=["POST"])
def mark_posted(draft_id):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute("UPDATE content_drafts SET status = ?, posted_at = ? WHERE id = ?",
                 ("posted", now, draft_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "draft_id": draft_id, "status": "posted"})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "growth-os-drafts-api"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)