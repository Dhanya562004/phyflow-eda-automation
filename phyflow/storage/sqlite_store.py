"""
SQLite Storage Adapter for PHYFlow Metadata Persistence.
Tracks run metadata, stage execution status, timing metrics, and artifact locations.
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from phyflow.models import RunMetadata


class SQLiteRunStore:
    """Provides persistent metadata storage and query capability using SQLite."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create runs database table if not exists."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    design_name TEXT NOT NULL,
                    corner TEXT NOT NULL,
                    status TEXT NOT NULL,
                    runtime_sec REAL NOT NULL,
                    execution_mode TEXT NOT NULL,
                    artifact_dir TEXT NOT NULL,
                    wns_ns REAL DEFAULT 0.0,
                    area_um2 REAL DEFAULT 0.0,
                    gate_count INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def record_run(self, meta: RunMetadata, wns_ns: float = 0.0, area_um2: float = 0.0, gate_count: int = 0) -> None:
        """Insert or replace run record in database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO runs (
                    run_id, timestamp, design_name, corner, status, runtime_sec,
                    execution_mode, artifact_dir, wns_ns, area_um2, gate_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meta.run_id,
                meta.timestamp,
                meta.design_name,
                meta.corner,
                meta.status,
                meta.runtime_sec,
                meta.execution_mode,
                meta.artifact_dir,
                wns_ns,
                area_um2,
                gate_count
            ))
            conn.commit()

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve historical run metadata records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT run_id, timestamp, design_name, corner, status, runtime_sec, execution_mode, wns_ns, area_um2, gate_count
                FROM runs
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Fetch details of a single run by run_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM runs WHERE run_id = ?", (run_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
