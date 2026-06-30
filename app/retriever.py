import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
from app.config import EMBED_MODEL, RERANK_MODEL, TOP_K_RETRIEVAL, TOP_K_RERANK
from app.ingest import load_index

# Load both models once at module level
embedder = SentenceTransformer(EMBED_MODEL)
reranker = CrossEncoder(RERANK_MODEL)


def embed_query(query: str) -> np.ndarray:
    """
    Embed the user query using the same model as ingestion.
    Returns normalised float32 vector of shape (1, dim).
    """
    vec = embedder.encode([query], convert_to_numpy=True).astype("float32")
    faiss.normalize_L2(vec)
    return vec


def retrieve(doc_id: str, query: str, top_k: int = TOP_K_RETRIEVAL) -> list[dict]:
    """
    Stage 1: bi-encoder retrieval via FAISS (fast, approximate).
    Returns top_k candidate chunks with their similarity scores.
    """
    index, chunks = load_index(doc_id)
    query_vec = embed_query(query)

    scores, indices = index.search(query_vec, min(top_k, index.ntotal))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = chunks[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)

    return results


def rerank(query: str, candidates: list[dict], top_k: int = TOP_K_RERANK) -> list[dict]:
    """
    Stage 2: cross-encoder re-ranking (slower, more accurate).
    Scores each (query, chunk) pair together for precise relevance.
    """
    if not candidates:
        return []

    pairs = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)

    for chunk, score in zip(candidates, scores):
        chunk["score"] = float(score)

    reranked = sorted(candidates, key=lambda x: x["score"], reverse=True)
    return reranked[:top_k]


def search(doc_id: str, query: str, top_k: int = TOP_K_RERANK) -> list[dict]:
    """
    Full two-stage retrieval pipeline:
      1. FAISS bi-encoder retrieval (top TOP_K_RETRIEVAL candidates)
      2. Cross-encoder re-ranking (returns top top_k)
    """
    candidates = retrieve(doc_id, query, top_k=TOP_K_RETRIEVAL)
    final = rerank(query, candidates, top_k=top_k)
    return final
