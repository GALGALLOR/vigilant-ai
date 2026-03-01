"""
Sentinel-Stream — SQLite Structured Event Store
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Stores all structured event data in a local SQLite database.
SQLite needs zero setup — file is created automatically on first use.

Complements Actian VectorAI (which stores embeddings + similarity search).
This store handles: filtering by time, alert stage, event type, pagination.

Tables:
  videos  — one row per uploaded/processed video
  events  — one row per 10s sub-clip
  tracks  — one row per person track (trajectory data)
"""

from __future__ import annotations
import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = Path("vigilant.db")   # sits in the backend/ root


# ─── Schema ───────────────────────────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS videos (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    duration_s      REAL,
    total_events    INTEGER DEFAULT 0,
    total_alerts    INTEGER DEFAULT 0,
    processing_time_s REAL,
    gpu             TEXT,
    upload_time     TEXT NOT NULL,
    chunks          INTEGER DEFAULT 0,
    subclips        INTEGER DEFAULT 0,
    cpu_time_s      REAL DEFAULT 0,
    gpu_time_s      REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS events (
    clip_id         TEXT PRIMARY KEY,
    video_id        TEXT NOT NULL,
    chunk_index     INTEGER,
    window_index    INTEGER,

    -- Millisecond timestamps
    start_ms        REAL,
    end_ms          REAL,
    duration_ms     REAL,
    first_detection_ms REAL,
    last_detection_ms  REAL,

    -- Legacy seconds (backward compat)
    start           REAL NOT NULL,
    end             REAL NOT NULL,
    duration        REAL,
    quality_score   REAL,

    -- Detection signals
    people_count    INTEGER DEFAULT 0,
    vehicle_count   INTEGER DEFAULT 0,
    peak_motion     REAL,
    mean_motion     REAL,
    contact_score   REAL,
    objects_json    TEXT,           -- JSON of expanded object counts

    -- Event semantics
    event_type      TEXT,
    event_confidence REAL,

    -- Alert
    alert_score     REAL DEFAULT 0,
    alert_stage     TEXT DEFAULT 'none',
    alert_reason    TEXT,

    -- Text
    caption         TEXT,
    tags            TEXT,           -- JSON array as string

    track_count     INTEGER DEFAULT 0,

    -- Full JSON blob (for API to return without reassembling)
    raw_json        TEXT NOT NULL,

    processed_at    TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

CREATE TABLE IF NOT EXISTS tracks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    clip_id         TEXT NOT NULL,
    track_id        TEXT NOT NULL,
    dwell_seconds   REAL,
    entry_ms        REAL,
    exit_ms         REAL,
    trajectory_json TEXT,          -- full trajectory as JSON
    FOREIGN KEY (clip_id) REFERENCES events(clip_id)
);

CREATE INDEX IF NOT EXISTS idx_events_video_id    ON events(video_id);
CREATE INDEX IF NOT EXISTS idx_events_alert_stage ON events(alert_stage);
CREATE INDEX IF NOT EXISTS idx_events_start       ON events(start);
CREATE INDEX IF NOT EXISTS idx_events_start_ms    ON events(start_ms);
CREATE INDEX IF NOT EXISTS idx_events_event_type  ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_alert_score ON events(alert_score DESC);
CREATE INDEX IF NOT EXISTS idx_tracks_clip_id     ON tracks(clip_id);

-- Gemini synthesis: holistic video understanding
CREATE TABLE IF NOT EXISTS video_summaries (
    video_id    TEXT PRIMARY KEY,
    summary     TEXT,
    intent      TEXT,       -- JSON array
    key_moments TEXT,       -- JSON array of {time, description}
    risk_level  TEXT DEFAULT 'medium',
    tags        TEXT,       -- JSON array
    created_at  TEXT,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);

-- Persistent chat history
CREATE TABLE IF NOT EXISTS chat_messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id    TEXT NOT NULL,
    role        TEXT NOT NULL,   -- 'user' or 'assistant'
    content     TEXT NOT NULL,
    results_json TEXT,           -- search results JSON if any
    created_at  TEXT NOT NULL,
    FOREIGN KEY (video_id) REFERENCES videos(id)
);
CREATE INDEX IF NOT EXISTS idx_chat_video ON chat_messages(video_id, created_at);
"""


def get_conn() -> sqlite3.Connection:
    """Return a connection to the SQLite DB, creating it if needed."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # better concurrent read performance
    return conn


def init_db() -> None:
    """Create tables and indexes. Safe to call multiple times (IF NOT EXISTS)."""
    with get_conn() as conn:
        conn.executescript(SCHEMA)
        # Migrate: add new columns to existing videos tables
        for col, typedef in [
            ("chunks",      "INTEGER DEFAULT 0"),
            ("subclips",    "INTEGER DEFAULT 0"),
            ("cpu_time_s",  "REAL DEFAULT 0"),
            ("gpu_time_s",  "REAL DEFAULT 0"),
        ]:
            try:
                conn.execute(f"ALTER TABLE videos ADD COLUMN {col} {typedef}")
            except Exception:
                pass  # column already exists
    print(f"✅ SQLite DB ready at {DB_PATH.resolve()}")


# ─── Videos ───────────────────────────────────────────────────────────────────

def insert_video(
    video_id: str,
    name: str,
    duration_s: float,
    total_events: int,
    total_alerts: int,
    processing_time_s: float,
    gpu: str,
    chunks: int = 0,
    subclips: int = 0,
    cpu_time_s: float = 0.0,
    gpu_time_s: float = 0.0,
) -> None:
    """Insert or replace a video record."""
    with get_conn() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO videos
              (id, name, duration_s, total_events, total_alerts,
               processing_time_s, gpu, upload_time,
               chunks, subclips, cpu_time_s, gpu_time_s)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            video_id, name, duration_s, total_events, total_alerts,
            processing_time_s, gpu, datetime.utcnow().isoformat() + "Z",
            chunks, subclips, cpu_time_s, gpu_time_s,
        ))


def list_videos() -> List[Dict]:
    """Return all videos ordered by most recent first."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM videos ORDER BY upload_time DESC"
        ).fetchall()
    return [dict(r) for r in rows]


# ─── Events ───────────────────────────────────────────────────────────────────

def insert_events(video_id: str, events: List[Dict[str, Any]]) -> int:
    """Batch-insert events. Handles both new and legacy JSON structures."""
    event_rows = []
    track_rows = []

    for e in events:
        # Handle new structure: event{} and alert{}
        ev = e.get("event", {})
        if not ev and e.get("events"):
            ev = e["events"][0]  # legacy fallback

        alert = e.get("alert", {})
        time_info = e.get("time", {})
        detections = e.get("detections", {})

        event_type = ev.get("label")
        event_conf = ev.get("confidence")

        # Build clean raw_json (strip _prefixed keys)
        raw = {k: v for k, v in e.items()
               if not k.startswith("_")}

        event_rows.append((
            e["clip_id"],
            video_id,
            e.get("chunk_index"),
            e.get("window_index"),
            time_info.get("start_ms"),
            time_info.get("end_ms"),
            time_info.get("duration_ms"),
            time_info.get("first_detection_ms"),
            time_info.get("last_detection_ms"),
            e.get("start"),
            e.get("end"),
            e.get("duration"),
            e.get("quality_score"),
            detections.get("people_count", e.get("people_count", 0)),
            detections.get("vehicle_count", e.get("vehicle_count", 0)),
            detections.get("peak_motion", e.get("evidence", {}).get("motion")),
            detections.get("mean_motion"),
            detections.get("contact_score", e.get("evidence", {}).get("overlap")),
            json.dumps(detections.get("objects")) if detections.get("objects") else None,
            event_type,
            event_conf,
            alert.get("score", e.get("alert_score", 0)),
            alert.get("stage", e.get("alert_stage", "none")),
            alert.get("reason", e.get("alert_reason")),
            e.get("caption"),
            json.dumps(e.get("tags", [])),
            e.get("track_count", len(e.get("tracks", []))),
            json.dumps(raw),
            e.get("processed_at"),
        ))

        # Insert track trajectories if present
        for traj in e.get("_track_trajectories", []):
            track_rows.append((
                e["clip_id"],
                traj["id"],
                None,  # dwell filled from track summary below
                None, None,
                json.dumps(traj.get("points", [])),
            ))

        # Update track rows with dwell/entry/exit from summaries
        for track in e.get("tracks", []):
            for tr in track_rows:
                if tr[0] == e["clip_id"] and tr[1] == track.get("id"):
                    idx = track_rows.index(tr)
                    track_rows[idx] = (
                        e["clip_id"],
                        track["id"],
                        track.get("dwell_seconds"),
                        track.get("entry_ms"),
                        track.get("exit_ms"),
                        tr[5],  # keep trajectory_json
                    )

    with get_conn() as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO events (
                clip_id, video_id, chunk_index, window_index,
                start_ms, end_ms, duration_ms, first_detection_ms, last_detection_ms,
                start, end, duration, quality_score,
                people_count, vehicle_count,
                peak_motion, mean_motion, contact_score, objects_json,
                event_type, event_confidence,
                alert_score, alert_stage, alert_reason,
                caption, tags, track_count,
                raw_json, processed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, event_rows)

        if track_rows:
            # Clear old tracks for these clips first
            clip_ids = list(set(r[0] for r in track_rows))
            conn.executemany("DELETE FROM tracks WHERE clip_id = ?",
                             [(cid,) for cid in clip_ids])
            conn.executemany("""
                INSERT INTO tracks (clip_id, track_id, dwell_seconds, entry_ms, exit_ms, trajectory_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, track_rows)

    return len(event_rows)


def get_events(
    video_id: Optional[str] = None,
    alert_stage: Optional[str] = None,
    event_type: Optional[str] = None,
    min_alert_score: Optional[float] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Dict]:
    """Retrieve events with optional filters. Returns parsed raw_json dicts."""
    clauses = []
    params: List = []

    if video_id is not None:
        clauses.append("video_id = ?")
        params.append(video_id)
    if alert_stage is not None:
        clauses.append("alert_stage = ?")
        params.append(alert_stage)
    if event_type is not None:
        clauses.append("event_type = ?")
        params.append(event_type)
    if min_alert_score is not None:
        clauses.append("alert_score >= ?")
        params.append(min_alert_score)

    where = " AND ".join(clauses) if clauses else "1=1"
    params += [limit, offset]

    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT raw_json FROM events WHERE {where} "
            f"ORDER BY start ASC LIMIT ? OFFSET ?",
            params,
        ).fetchall()

    return [json.loads(r["raw_json"]) for r in rows]


def get_event_by_id(clip_id: str) -> Optional[Dict]:
    """Get a single event by clip_id."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT raw_json FROM events WHERE clip_id = ?", (clip_id,)
        ).fetchone()
    return json.loads(row["raw_json"]) if row else None


def get_alerts(video_id: Optional[str] = None, top_k: int = 50) -> List[Dict]:
    """Return top alerts, sorted by alert_score desc."""
    if video_id:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM events "
                "WHERE video_id = ? AND alert_stage != 'none' "
                "ORDER BY alert_score DESC LIMIT ?",
                (video_id, top_k),
            ).fetchall()
    else:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM events "
                "WHERE alert_stage != 'none' "
                "ORDER BY alert_score DESC LIMIT ?",
                (top_k,),
            ).fetchall()
    return [json.loads(r["raw_json"]) for r in rows]


def search_events_text(
    query: str,
    video_id: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    """Full-text search over captions and tags."""
    q = f"%{query.lower()}%"
    if video_id:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM events "
                "WHERE video_id = ? AND (LOWER(caption) LIKE ? OR LOWER(tags) LIKE ?) "
                "ORDER BY alert_score DESC LIMIT ?",
                (video_id, q, q, limit),
            ).fetchall()
    else:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT raw_json FROM events "
                "WHERE LOWER(caption) LIKE ? OR LOWER(tags) LIKE ? "
                "ORDER BY alert_score DESC LIMIT ?",
                (q, q, limit),
            ).fetchall()
    return [json.loads(r["raw_json"]) for r in rows]


def get_timeline(video_id: Optional[str] = None) -> List[Dict]:
    """Compact timeline data for the frontend (one marker per event)."""
    if video_id:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT clip_id, start, end, start_ms, end_ms, "
                "alert_stage, alert_score, event_type, people_count, track_count "
                "FROM events WHERE video_id = ? ORDER BY start ASC",
                (video_id,),
            ).fetchall()
    else:
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT clip_id, start, end, start_ms, end_ms, "
                "alert_stage, alert_score, event_type, people_count, track_count "
                "FROM events ORDER BY start ASC"
            ).fetchall()
    return [dict(r) for r in rows]


def get_stats() -> Dict[str, Any]:
    """Overall pipeline stats."""
    with get_conn() as conn:
        videos = conn.execute("SELECT COUNT(*) as n FROM videos").fetchone()
        events = conn.execute("SELECT COUNT(*) as n FROM events").fetchone()
        alerts = conn.execute(
            "SELECT COUNT(*) as n FROM events WHERE alert_stage != 'none'"
        ).fetchone()
        tracks = conn.execute("SELECT COUNT(*) as n FROM tracks").fetchone()
        latest = conn.execute(
            "SELECT * FROM videos ORDER BY upload_time DESC LIMIT 1"
        ).fetchone()

    return {
        "total_videos": videos["n"],
        "total_events": events["n"],
        "total_alerts": alerts["n"],
        "total_tracks": tracks["n"],
        "latest_video": dict(latest) if latest else None,
    }


# ─── Video Summaries ──────────────────────────────────────────────────────────

def save_video_summary(video_id: str, synthesis: Dict) -> None:
    """Save Gemini synthesis result."""
    from datetime import datetime
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO video_summaries "
            "(video_id, summary, intent, key_moments, risk_level, tags, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                video_id,
                synthesis.get("summary", ""),
                json.dumps(synthesis.get("intent", [])),
                json.dumps(synthesis.get("key_moments", [])),
                synthesis.get("risk_level", "medium"),
                json.dumps(synthesis.get("tags", [])),
                datetime.utcnow().isoformat() + "Z",
            ),
        )


def get_video_summary(video_id: str) -> Optional[Dict]:
    """Get Gemini synthesis result for a video."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM video_summaries WHERE video_id = ?", (video_id,)
        ).fetchone()
    if not row:
        return None
    return {
        "video_id": row["video_id"],
        "summary": row["summary"],
        "intent": json.loads(row["intent"] or "[]"),
        "key_moments": json.loads(row["key_moments"] or "[]"),
        "risk_level": row["risk_level"],
        "tags": json.loads(row["tags"] or "[]"),
        "created_at": row["created_at"],
    }


# ─── Chat Messages ────────────────────────────────────────────────────────────

def save_chat_message(video_id: str, role: str, content: str, results_json: str = None) -> int:
    """Save a chat message (user or assistant). Returns message ID."""
    from datetime import datetime
    with get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO chat_messages (video_id, role, content, results_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (video_id, role, content, results_json, datetime.utcnow().isoformat() + "Z"),
        )
        return cursor.lastrowid


def get_chat_history(video_id: str, limit: int = 50) -> List[Dict]:
    """Get chat history for a video, ordered by time."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, role, content, results_json, created_at "
            "FROM chat_messages WHERE video_id = ? "
            "ORDER BY created_at ASC LIMIT ?",
            (video_id, limit),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "role": r["role"],
            "content": r["content"],
            "results": json.loads(r["results_json"]) if r["results_json"] else None,
            "created_at": r["created_at"],
        }
        for r in rows
    ]


# ─── CLI test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("✅ SQLite schema created")
    print(f"   DB file: {DB_PATH.resolve()}")
