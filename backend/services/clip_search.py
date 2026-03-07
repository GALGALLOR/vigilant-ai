"""
Vigilant-AI — CLIP Semantic Search Service
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Smart search over video events. Uses a multi-strategy approach:

  Strategy 1: CLIP text-to-image KNN (VectorAI) — understands visual meaning
  Strategy 2: Caption semantic search (fuzzy text matching) — catches keyword intent
  Strategy 3: Query expansion — "shoplifting" → also searches "stealing", "theft", etc.

Results merged and ranked by relevance.
"""

from __future__ import annotations
import os, re
from typing import List, Dict, Any, Optional
from pathlib import Path

# ─── Query Expansion ─────────────────────────────────────────────────────────
# Maps user intent to related visual/textual terms for better recall.

QUERY_EXPANSIONS: Dict[str, List[str]] = {
    "shoplifting": ["stealing", "theft", "taking items", "concealing", "hiding", "pocketing", "under jacket", "store", "merchandise", "grab"],
    "stealing": ["shoplifting", "theft", "taking", "grab", "concealing", "hiding", "snatch", "pocketing"],
    "theft": ["stealing", "shoplifting", "taking items", "grab", "snatch", "hiding", "concealing", "pocketing", "under jacket"],
    "fighting": ["physical altercation", "punching", "hitting", "altercation", "assault", "attack", "violence"],
    "violence": ["fighting", "altercation", "assault", "attack", "physical", "aggressive"],
    "assault": ["attack", "fighting", "hitting", "physical altercation", "violence"],
    "trespassing": ["unauthorized", "restricted area", "breach", "intrusion", "entering"],
    "loitering": ["standing", "waiting", "lingering", "idle", "staying"],
    "suspicious": ["unusual", "strange", "abnormal", "odd", "watching", "lurking"],
    "weapon": ["knife", "gun", "armed", "threatening"],
    "falling": ["fell", "fallen", "collapse", "on the ground", "slip", "trip"],
    "medical": ["injured", "hurt", "fallen", "emergency", "collapse"],
    "running": ["fast", "sprint", "fleeing", "escape", "rushing"],
    "crowd": ["group", "gathering", "multiple people", "many people"],
    "alone": ["single person", "one person", "solitary", "by themselves"],
    "vehicle": ["car", "truck", "van", "driving"],
    "break in": ["breaking", "forcing entry", "breaking door", "smashing"],
    "fire": ["smoke", "flames", "burning"],
}


def _expand_query(query: str) -> List[str]:
    """Expand a query with related terms for better recall."""
    query_lower = query.lower().strip()
    expansions = [query]

    for key, terms in QUERY_EXPANSIONS.items():
        if key in query_lower or query_lower in key:
            expansions.extend(terms)

    return list(dict.fromkeys(expansions))  # deduplicate, preserve order


# ─── CLIP Text Encoder ───────────────────────────────────────────────────────

_clip_model = None
_clip_processor = None
_clip_unavailable_reason: Optional[str] = None
_clip_warned_unavailable = False

CLIP_MODEL_ID = "openai/clip-vit-large-patch14"
CACHE_DIR = Path(__file__).parent.parent / ".clip_cache"


def _load_clip():
    global _clip_model, _clip_processor, _clip_unavailable_reason
    if _clip_model is not None:
        return
    if _clip_unavailable_reason:
        raise RuntimeError(_clip_unavailable_reason)

    try:
        import torch
        from transformers import CLIPModel, CLIPProcessor
    except ModuleNotFoundError as e:
        _clip_unavailable_reason = (
            f"missing optional dependency '{e.name}' "
            "(install torch + transformers to enable semantic CLIP search)"
        )
        raise RuntimeError(_clip_unavailable_reason) from e

    os.makedirs(CACHE_DIR, exist_ok=True)
    os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    print("Loading CLIP text encoder (CPU)...")

    _clip_model = CLIPModel.from_pretrained(CLIP_MODEL_ID, cache_dir=str(CACHE_DIR))
    _clip_model.eval()
    _clip_processor = CLIPProcessor.from_pretrained(CLIP_MODEL_ID, cache_dir=str(CACHE_DIR))
    print("CLIP text encoder loaded")


def encode_text(query: str) -> List[float]:
    """Encode a text query into a 768-dim CLIP vector (L2-normalized)."""
    import torch
    _load_clip()
    inputs = _clip_processor(text=[query], return_tensors="pt", padding=True,
                              truncation=True, max_length=77)
    with torch.no_grad():
        # Use text_model + text_projection directly — same reason as vision side:
        # get_text_features() has version-dependent return types.
        #   text_model -> pooler_output: [1, 768] (EOS token, text hidden size = 768)
        #   text_projection: Linear(768 → 768) -> [1, 768]
        text_out = _clip_model.text_model(**inputs)
        pooled   = text_out.pooler_output              # [1, 768]
        feats    = _clip_model.text_projection(pooled) # [1, 768]
        feats    = feats.squeeze(0)                    # [768]
        feats    = feats / feats.norm()                # L2 normalize
    vector = feats.cpu().float().tolist()
    assert len(vector) == 768 and isinstance(vector[0], float), (
        f"CLIP text encode: expected 768 floats, got len={len(vector)}"
    )
    return vector


# ─── Search Functions ────────────────────────────────────────────────────────

def _search_vectorai(query: str, video_id: Optional[str], top_k: int) -> List[Dict]:
    """CLIP vector KNN search via VectorAI."""
    global _clip_warned_unavailable
    try:
        query_vector = encode_text(query)
        from services.vectordb import search_by_vector
        results = search_by_vector(query_vector=query_vector, top_k=top_k * 2)
        if video_id:
            results = [r for r in results if r.get("payload", {}).get("video_source", "").replace(".", "_").replace(" ", "_") == video_id
                       or r.get("video_id") == video_id]
        return results[:top_k]
    except RuntimeError as e:
        # Keep chat usable via caption search when local CLIP deps are absent.
        if not _clip_warned_unavailable:
            print(f"VectorAI semantic search disabled: {e}")
            _clip_warned_unavailable = True
        return []
    except Exception as e:
        print(f"VectorAI search error: {e}")
        return []


def _search_captions(query: str, video_id: Optional[str], top_k: int) -> List[Dict]:
    """Search event captions in SQLite using expanded query terms."""
    try:
        from services.db import search_events_text
        all_terms = _expand_query(query)
        results = []
        seen = set()
        for term in all_terms[:6]:  # limit to top 6 expansions
            hits = search_events_text(query=term, video_id=video_id, limit=top_k)
            for h in hits:
                cid = h.get("clip_id", "")
                if cid not in seen:
                    seen.add(cid)
                    h["search_method"] = "caption"
                    h["similarity"] = 0.0
                    results.append(h)
        return results[:top_k]
    except Exception as e:
        print(f"Caption search error: {e}")
        return []


def hybrid_search(
    query: str,
    video_id: Optional[str] = None,
    top_k: int = 10,
) -> List[Dict[str, Any]]:
    """
    Multi-strategy search (parallel):
      1. CLIP vector KNN (semantic visual matching)       — runs concurrently
      2. Caption text search with query expansion         — runs concurrently
    Results merged and deduplicated.
    """
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=2) as ex:
        fut_sem = ex.submit(_search_vectorai, query, video_id, top_k)
        fut_cap = ex.submit(_search_captions, query, video_id, top_k)
        semantic_results = fut_sem.result()
        caption_results  = fut_cap.result()

    # Merge: semantic first, then caption hits not already present
    seen_ids: set = set()
    merged: List[Dict] = []

    for r in semantic_results:
        cid = r.get("clip_id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            r["search_method"] = "semantic"
            merged.append(r)

    for r in caption_results:
        cid = r.get("clip_id", "")
        if cid and cid not in seen_ids:
            seen_ids.add(cid)
            merged.append(r)

    return merged[:top_k]
