# BM25 + FAISS

# app/services/retriever.py 
import os, json
import numpy as np
from rank_bm25 import BM25Okapi
import faiss
from typing import List, Dict, Any, Optional, Tuple
from app.core.config import settings
from app.services.embedder import encode

# FAISS files
_FAISS_INDEX = os.path.join(settings.FAISS_DIR, "index.faiss")
_FAISS_META  = os.path.join(settings.FAISS_DIR, "meta.json")

# Cache
_bm25 = None
_bm25_texts: list[str] = []
_faiss_index = None
_meta: list[dict] = []

def _load_faiss():
    global _faiss_index, _meta
    if _faiss_index is None and os.path.exists(_FAISS_INDEX):
        _faiss_index = faiss.read_index(_FAISS_INDEX)
    if not _meta and os.path.exists(_FAISS_META):
        with open(_FAISS_META, "r", encoding="utf-8") as f:
            _meta = json.load(f)

def _build_bm25():
    global _bm25, _bm25_texts
    if _bm25 is not None: return
    if not _meta:
        _load_faiss()
    _bm25_texts = [m["text"] for m in _meta]
    tokenized = [t.lower().split() for t in _bm25_texts]
    _bm25 = BM25Okapi(tokenized)

def _search_bm25(query: str, k: int) -> List[Tuple[int, float]]:
    _build_bm25()
    scores = _bm25.get_scores(query.lower().split())
    idxs = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[int(i)])) for i in idxs if scores[int(i)] > 0]

def _search_faiss(query: str, k: int) -> List[Tuple[int, float]]:
    _load_faiss()
    if _faiss_index is None:
        return []
    qv = np.array(encode([query])[0], dtype="float32")[None, :]
    D, I = _faiss_index.search(qv, k)
    return [(int(i), float(1 - D[0][j])) for j, i in enumerate(I[0]) if i >= 0]
    # note: if index uses inner-product, adjust scoring accordingly

def hybrid_search(query: str, article_id: Optional[int], filters: Optional[Dict[str, Any]]) -> List[dict]:
    """
    Returns list of {articleId, chunk_idx, text, score}
    If article_id provided, filter candidates to that article only.
    """
    _load_faiss()
    # run both
    bm = _search_bm25(query, settings.TOP_K_BM25)
    ve = _search_faiss(query, settings.TOP_K_VEC)

    # merge by linear weighted score
    alpha = settings.HYBRID_ALPHA
    scores: dict[int, float] = {}
    for i, s in bm: scores[i] = scores.get(i, 0.0) + (1-alpha) * (s if s>0 else 0)
    for i, s in ve: scores[i] = scores.get(i, 0.0) + alpha * (s if s>0 else 0)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    out: list[dict] = []
    for idx, sc in ranked:
        if idx < 0 or idx >= len(_meta): continue
        m = _meta[idx]
        if article_id is not None and m.get("articleId") != article_id:
            continue
        # filters ví dụ: {"categoryId": 3, "lang":"vi"}
        if filters:
            ok = True
            for k, v in filters.items():
                if str(m.get(k)) != str(v): ok = False; break
            if not ok: continue
        out.append({"articleId": m["articleId"], "chunk_idx": m["chunk_idx"], "text": m["text"], "score": sc})
        if len(out) >= settings.TOP_K_FINAL: break
    return out


# Chuẩn bị FAISS meta: meta.json là list các object:
# [{"articleId": 123, "chunk_idx": 0, "text": "đoạn văn ..."}, ...]
# index.faiss chứa vectors (embedding dim = EMBED_DIM). 
# Có thể build offline (ETL) từ bảng article_chunks của backend.