#!/usr/bin/env python3
"""Content drafts store — SQLite queue for ghost writer pipeline.

States: draft → reviewed → approved → posted → failed
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import sqlite3
import json
from datetime import datetime, timezone
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "strategic_memory" / "growth_os.db"


def _get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_drafts_table():
    """Create content_drafts table if not exists."""
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS content_drafts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform TEXT NOT NULL,          -- 'linkedin' or 'twitter'
            draft_text TEXT NOT NULL,
            topic TEXT,
            signal_sources TEXT,            -- JSON list of signal URLs
            vault_context TEXT,              -- JSON of vault examples used
            status TEXT DEFAULT 'draft',    -- draft | reviewed | approved | posted | rejected
            generated_at TEXT NOT NULL,
            reviewed_at TEXT,
            reviewed_by TEXT DEFAULT 'telegram',
            approved_at TEXT,
            posted_at TEXT,
            error_msg TEXT,
            engagement_impressions INTEGER,
            engagement_likes INTEGER,
            engagement_comments INTEGER,
            UNIQUE(platform, topic, generated_at)
        )
    """)
    conn.commit()
    conn.close()


def save_draft(platform: str, draft_text: str, topic: str,
               signal_sources: list[str] = None,
               vault_context: dict = None) -> int:
    """Save a new content draft. Returns draft ID."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO content_drafts
        (platform, draft_text, topic, signal_sources, vault_context, generated_at, status)
        VALUES (?, ?, ?, ?, ?, ?, 'draft')
    """, (
        platform,
        draft_text,
        topic,
        json.dumps(signal_sources or []),
        json.dumps(vault_context or {}),
        datetime.now(timezone.utc).isoformat(),
    ))
    draft_id = cur.lastrowid
    conn.commit()
    conn.close()
    return draft_id


def get_draft(draft_id: int) -> Optional[dict]:
    """Get a draft by ID."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM content_drafts WHERE id = ?", (draft_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_drafts_by_status(status: str, platform: str = None, limit: int = 10) -> list[dict]:
    """Get drafts by status, optionally filtered by platform."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    if platform:
        cur.execute(
            "SELECT * FROM content_drafts WHERE status = ? AND platform = ? ORDER BY generated_at DESC LIMIT ?",
            (status, platform, limit)
        )
    else:
        cur.execute(
            "SELECT * FROM content_drafts WHERE status = ? ORDER BY generated_at DESC LIMIT ?",
            (status, limit)
        )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_review(platform: str = None, limit: int = 5) -> list[dict]:
    """Get drafts ready for review (status = draft or reviewed)."""
    return get_drafts_by_status("draft", platform, limit) + get_drafts_by_status("reviewed", platform, limit)


def update_draft_status(draft_id: int, status: str, error_msg: str = None) -> None:
    """Update draft status."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    if status == "reviewed":
        cur.execute("UPDATE content_drafts SET status = ?, reviewed_at = ?, reviewed_by = 'telegram' WHERE id = ?",
                    (status, now, draft_id))
    elif status == "approved":
        cur.execute("UPDATE content_drafts SET status = ?, approved_at = ? WHERE id = ?",
                    (status, now, draft_id))
    elif status == "posted":
        cur.execute("UPDATE content_drafts SET status = ?, posted_at = ? WHERE id = ?",
                    (status, now, draft_id))
    elif status == "rejected":
        cur.execute("UPDATE content_drafts SET status = ?, reviewed_at = ? WHERE id = ?",
                    (status, now, draft_id))
    elif status == "failed":
        cur.execute("UPDATE content_drafts SET status = ?, error_msg = ? WHERE id = ?",
                    (status, error_msg or "", draft_id))
    conn.commit()
    conn.close()


def mark_posted(draft_id: int, impressions: int = 0, likes: int = 0, comments: int = 0) -> None:
    """Mark a draft as posted with engagement metrics."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE content_drafts
        SET status = 'posted', posted_at = ?, engagement_impressions = ?,
            engagement_likes = ?, engagement_comments = ?
        WHERE id = ?
    """, (datetime.now(timezone.utc).isoformat(), impressions, likes, comments, draft_id))
    conn.commit()
    conn.close()


def get_content_stats(days: int = 30) -> dict:
    """Get content pipeline stats for last N days."""
    init_drafts_table()
    conn = _get_db()
    cur = conn.cursor()
    cutoff = datetime.now(timezone.utc).isoformat()
    from datetime import timedelta
    cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

    cur.execute("""
        SELECT status, COUNT(*) as count FROM content_drafts
        WHERE generated_at >= ? GROUP BY status
    """, (cutoff_date,))
    status_counts = dict(cur.fetchall())

    cur.execute("""
        SELECT platform, COUNT(*) as count FROM content_drafts
        WHERE generated_at >= ? GROUP BY platform
    """, (cutoff_date,))
    platform_counts = dict(cur.fetchall())

    conn.close()
    return {
        "period_days": days,
        "status_breakdown": status_counts,
        "platform_breakdown": platform_counts,
        "total_generated": sum(status_counts.values()),
    }


if __name__ == "__main__":
    init_drafts_table()
    print("Content drafts store initialized")

    # Test save
    draft_id = save_draft(
        platform="linkedin",
        draft_text="Test draft content",
        topic="fintech_growth",
        signal_sources=["https://news.google.com/...", "https://reddit.com/..."],
        vault_context={"topics": ["lending", "credit"], "examples": 3}
    )
    print(f"Saved draft ID: {draft_id}")

    stats = get_content_stats(days=7)
    print(f"Stats (7 days): {stats}")