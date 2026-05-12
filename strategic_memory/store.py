"""SQLite-backed strategic memory store.

Three stores in one db:
- signals: raw market signals with interpretations
- theses: recurring strategic beliefs
- predictions: testable hypotheses with outcomes
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

from config import get_db_path


def _json_default(obj):
    """JSON serializer for datetime and other non-serializable types."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


class BaseStore:
    """Base class for SQLite-backed stores."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db_path = get_db_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize the database schema."""
        raise NotImplementedError


class SignalStore(BaseStore):
    """Store and retrieve market signals."""

    def __init__(self):
        super().__init__("signals")

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    source TEXT NOT NULL,
                    category TEXT DEFAULT 'manual_observation',
                    url TEXT,
                    collected_at TEXT NOT NULL,
                    metadata TEXT DEFAULT '{}',
                    interpretation TEXT,
                    strategic_weight REAL,
                    tags TEXT DEFAULT '[]',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_signals_collected
                ON signals(collected_at DESC)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_signals_category
                ON signals(category)
            """)

    def add_signal(self, signal) -> int:
        """Add a signal to the store. Returns the signal id."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO signals
                (text, source, category, url, collected_at, metadata, interpretation,
                 strategic_weight, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signal.text,
                    signal.source,
                    signal.category,
                    signal.url,
                    signal.collected_at.isoformat(),
                    json.dumps(signal.metadata, default=_json_default),
                    signal.interpretation,
                    signal.strategic_weight,
                    json.dumps(signal.tags),
                ),
            )
            conn.commit()
            return cursor.lastrowid

    def get_recent(self, limit: int = 50, category: Optional[str] = None) -> list:
        """Get recent signals, optionally filtered by category."""
        with self._get_conn() as conn:
            if category:
                rows = conn.execute(
                    """
                    SELECT * FROM signals
                    WHERE category = ?
                    ORDER BY collected_at DESC
                    LIMIT ?
                    """,
                    (category, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT * FROM signals
                    ORDER BY collected_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()

            return [dict(row) for row in rows]

    def get_unprocessed(self, limit: int = 50) -> list:
        """Get signals that haven't been interpreted yet."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM signals
                WHERE interpretation IS NULL
                ORDER BY collected_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def update_interpretation(self, signal_id: int, interpretation: str,
                             weight: float, tags: list[str]):
        """Update a signal with its interpretation."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE signals
                SET interpretation = ?, strategic_weight = ?, tags = ?
                WHERE id = ?
                """,
                (interpretation, weight, json.dumps(tags), signal_id),
            )
            conn.commit()


class ThesisStore(BaseStore):
    """Store recurring strategic theses."""

    def __init__(self):
        super().__init__("theses")

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS theses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thesis_text TEXT NOT NULL,
                    thesis_type TEXT DEFAULT 'belief',
                    confidence REAL DEFAULT 0.5,
                    evidence TEXT DEFAULT '[]',
                    invalidated_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_thesis(self, thesis_text: str, thesis_type: str = "belief",
                   confidence: float = 0.5, evidence: Optional[list] = None) -> int:
        """Add a new thesis or hypothesis."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO theses (thesis_text, thesis_type, confidence, evidence)
                VALUES (?, ?, ?, ?)
                """,
                (thesis_text, thesis_type, confidence, json.dumps(evidence or [])),
            )
            conn.commit()
            return cursor.lastrowid

    def invalidate(self, thesis_id: int):
        """Mark a thesis as invalidated."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE theses
                SET invalidated_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), thesis_id),
            )
            conn.commit()

    def get_active(self) -> list:
        """Get all non-invalidated theses."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM theses
                WHERE invalidated_at IS NULL
                ORDER BY updated_at DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]


class PredictionStore(BaseStore):
    """Store testable predictions with outcomes."""

    def __init__(self):
        super().__init__("predictions")

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_text TEXT NOT NULL,
                    outcome TEXT,
                    outcome_correct TEXT,
                    resolve_by TEXT,
                    resolved_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def add_prediction(self, prediction_text: str, resolve_by: Optional[str] = None) -> int:
        """Add a new prediction."""
        with self._get_conn() as conn:
            cursor = conn.execute(
                """
                INSERT INTO predictions (prediction_text, resolve_by)
                VALUES (?, ?)
                """,
                (prediction_text, resolve_by),
            )
            conn.commit()
            return cursor.lastrowid

    def resolve(self, prediction_id: int, outcome: str, correct: bool):
        """Mark a prediction as resolved with its outcome."""
        with self._get_conn() as conn:
            conn.execute(
                """
                UPDATE predictions
                SET outcome = ?, outcome_correct = ?, resolved_at = ?
                WHERE id = ?
                """,
                (outcome, "true" if correct else "false", datetime.utcnow().isoformat(), prediction_id),
            )
            conn.commit()

    def get_pending(self) -> list:
        """Get unresolved predictions."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM predictions
                WHERE outcome IS NULL
                ORDER BY created_at DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def get_resolved(self, limit: int = 50) -> list:
        """Get recently resolved predictions."""
        with self._get_conn() as conn:
            rows = conn.execute(
                """
                SELECT * FROM predictions
                WHERE outcome IS NOT NULL
                ORDER BY resolved_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]