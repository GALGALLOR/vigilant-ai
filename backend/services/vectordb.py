"""
Vigilant-AI — Actian VectorAI DB Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Wraps the actiancortex Python client for:
  - Storing CLIP embeddings (768-dim) per event
  - Similarity search by text query or event ID
  - Filtered search (by event type, alert stage, time range)

Prerequisites:
  docker compose up -d    # starts VectorAI DB on localhost:50051
  pip install ./actiancortex-0.1.0b1-py3-none-any.whl

Collection layout:
  name      : "vigilant_events"
  dimension : 768   (CLIP ViT-L/14 output)
  metric    : COSINE
  payload   : full EventJSON fields (except the embedding itself)
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional

# ─── Config ───────────────────────────────────────────────────────────────────
VECTORDB_HOST     = "localhost:50051"
COLLECTION_NAME   = "vigilant_events"
EMBEDDING_DIM     = 768                    # CLIP ViT-L/14
DISTANCE_METRIC   = "COSINE"               # best for CLIP embeddings
DEFAULT_TOP_K     = 10


def _get_client():
    """Return a connected CortexClient. Import inside fn so it's not a local dep."""
    from cortex import CortexClient, DistanceMetric
    return CortexClient(VECTORDB_HOST), DistanceMetric


# ─── Collection Setup ─────────────────────────────────────────────────────────

def ensure_collection() -> None:
    """
    Create the 'vigilant_events' collection if it doesn't exist yet.
    Safe to call multiple times (idempotent).
    """
    from cortex import CortexClient, DistanceMetric

    with CortexClient(VECTORDB_HOST) as client:
        version, uptime = client.health_check()
        print(f"✅ Actian VectorAI connected | version={version} uptime={uptime:.0f}s")

        if not client.has_collection(COLLECTION_NAME):
            client.create_collection(
                name            = COLLECTION_NAME,
                dimension       = EMBEDDING_DIM,
                distance_metric = DistanceMetric.COSINE,
            )
            print(f"✅ Collection '{COLLECTION_NAME}' created (dim={EMBEDDING_DIM}, COSINE)")
        else:
            print(f"ℹ️  Collection '{COLLECTION_NAME}' already exists")


# ─── Ingest ───────────────────────────────────────────────────────────────────

def ingest_events(events: List[Dict[str, Any]]) -> int:
    """
    Batch-insert a list of EventJSON dicts into VectorAI DB.
    Each event must have a 'clip_embedding' (768-dim list) and 'clip_id'.

    Returns number of events successfully inserted.
    """
    from cortex import CortexClient

    # Filter out events with no embedding (processing errors)
    valid = [e for e in events
             if e.get("_clip_embedding") and len(e["_clip_embedding"]) == EMBEDDING_DIM]
    if not valid:
        # Fallback: try legacy key
        valid = [e for e in events
                 if e.get("clip_embedding") and len(e["clip_embedding"]) == EMBEDDING_DIM]
    if not valid:
        print("⚠️  No valid embeddings to insert")
        return 0

    # Build ids, vectors, payloads
    # VectorAI requires integer IDs — we derive a stable int from clip_id
    ids:      List[int]        = []
    vectors:  List[List[float]] = []
    payloads: List[Dict]       = []

    for e in valid:
        # clip_id format: "c00_w0003" → hash to stable int
        vec_id = abs(hash(e["clip_id"])) % (2**31)
        ids.append(vec_id)
        vectors.append(e.get("_clip_embedding") or e.get("clip_embedding"))

        # Payload = everything except heavy fields
        payload = {k: v for k, v in e.items()
                   if not k.startswith("_") and k != "clip_embedding"}
        # Flatten nested dicts for VectorAI payload
        if "event" in payload and isinstance(payload["event"], dict):
            payload["event_label"] = payload["event"].get("label", "")
            payload["event_confidence"] = payload["event"].get("confidence", 0)
        if "alert" in payload and isinstance(payload["alert"], dict):
            payload["alert_score"] = payload["alert"].get("score", 0)
            payload["alert_stage"] = payload["alert"].get("stage", "none")
        if "time" in payload and isinstance(payload["time"], dict):
            payload["start_ms"] = payload["time"].get("start_ms")
            payload["end_ms"] = payload["time"].get("end_ms")
        payloads.append(payload)

    with CortexClient(VECTORDB_HOST) as client:
        client.batch_upsert(
            COLLECTION_NAME,
            ids      = ids,
            vectors  = vectors,
            payloads = payloads,
        )
        client.flush(COLLECTION_NAME)

    print(f"✅ Inserted {len(valid)} events into VectorAI (skipped {len(events)-len(valid)} errors)")
    return len(valid)


# ─── Search ───────────────────────────────────────────────────────────────────

def search_by_vector(
    query_vector: List[float],
    top_k: int = DEFAULT_TOP_K,
    min_alert_score: Optional[float] = None,
    event_type: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Find the top-k most similar events to a query embedding.
    Optionally filter by minimum alert_score or event_type label.

    Returns list of result dicts (payload + similarity score).
    """
    from cortex import CortexClient
    from cortex.filters import Filter, Field

    with CortexClient(VECTORDB_HOST) as client:
        # Build optional Filter DSL
        if min_alert_score is not None or event_type is not None:
            f = Filter()
            if min_alert_score is not None:
                f = f.must(Field("alert_score").range(gte=float(min_alert_score)))
            if event_type is not None:
                # event_type stored as first label in events_json string
                f = f.must(Field("events_json").eq(event_type))
            results = client.search_filtered(COLLECTION_NAME, query_vector, f, top_k=top_k)
        else:
            results = client.search(COLLECTION_NAME, query_vector, top_k=top_k)

    return [
        {
            "clip_id":     r.payload.get("clip_id"),
            "start":       r.payload.get("start"),
            "end":         r.payload.get("end"),
            "caption":     r.payload.get("caption"),
            "alert_score": r.payload.get("alert_score"),
            "alert_stage": r.payload.get("alert_stage"),
            "similarity":  round(float(r.score), 4),
            "payload":     r.payload,
        }
        for r in results
    ]


def search_similar_to_event(
    clip_id: str,
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    'Find similar events' — given a clip_id, find the most similar events.
    Retrieves the stored vector by ID then searches for nearest neighbours.
    """
    from cortex import CortexClient

    vec_id = abs(hash(clip_id)) % (2**31)
    with CortexClient(VECTORDB_HOST) as client:
        record = client.get(COLLECTION_NAME, vec_id)
        if record is None:
            return []
        # Exclude itself from results
        candidates = client.search(COLLECTION_NAME, record.vector, top_k=top_k + 1)
        return [
            {
                "clip_id":    r.payload.get("clip_id"),
                "start":      r.payload.get("start"),
                "end":        r.payload.get("end"),
                "caption":    r.payload.get("caption"),
                "similarity": round(float(r.score), 4),
            }
            for r in candidates
            if r.payload.get("clip_id") != clip_id   # exclude self
        ][:top_k]


# ─── Stats ────────────────────────────────────────────────────────────────────

def collection_stats() -> Dict[str, Any]:
    """Return basic stats about the vigilant_events collection."""
    from cortex import CortexClient
    with CortexClient(VECTORDB_HOST) as client:
        stats = client.get_stats(COLLECTION_NAME)
        count = client.count(COLLECTION_NAME)
        return {"collection": COLLECTION_NAME, "count": count, "stats": str(stats)}


# ─── CLI test ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔌 Testing Actian VectorAI connection...")
    ensure_collection()
    stats = collection_stats()
    print(f"📊 Collection stats: {stats}")
    print("✅ VectorAI DB test passed")
