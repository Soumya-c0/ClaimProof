import os
from typing import List
from rank_bm25 import BM25Okapi

# CLAIMPROOF_LIGHT=1 -> BM25-only retrieval (no ChromaDB, torch or reranker) for small free hosts.
LIGHT = os.getenv("CLAIMPROOF_LIGHT") == "1"

if not LIGHT:
    import chromadb
    from sentence_transformers import CrossEncoder

    _chroma_client = chromadb.Client()
    _collection = _chroma_client.get_or_create_collection(name="policy_clauses")
    _reranker = CrossEncoder("BAAI/bge-reranker-base")
else:
    _collection = None
    _reranker = None

_stored_clauses: List[str] = []
_bm25_index = None


def index_policy_clauses(clauses: List[str]) -> None:
    """Stores tokenized policy clauses in BM25 (and ChromaDB when not in light mode)."""
    global _stored_clauses, _bm25_index
    _stored_clauses = clauses

    if clauses:
        if _collection is not None:
            _collection.upsert(
                documents=clauses,
                ids=[f"clause_{i}" for i in range(len(clauses))],
            )
        tokenized_corpus = [c.lower().split() for c in clauses]
        _bm25_index = BM25Okapi(tokenized_corpus)


def hybrid_retrieve(query: str, top_k: int = 3) -> List[str]:
    """
    Full mode: ChromaDB semantic search + BM25 keyword search, reranked with BGE.
    Light mode: BM25 keyword search only.
    """
    if not _stored_clauses:
        return []

    semantic_docs: List[str] = []
    if _collection is not None:
        vector_hits = _collection.query(query_texts=[query], n_results=min(top_k, len(_stored_clauses)))
        semantic_docs = vector_hits["documents"][0] if vector_hits.get("documents") else []

    keyword_docs: List[str] = []
    if _bm25_index:
        scores = _bm25_index.get_scores(query.lower().split())
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        keyword_docs = [_stored_clauses[i] for i in top_indices]

    candidates = list(dict.fromkeys(semantic_docs + keyword_docs))
    if not candidates:
        return []

    if _reranker is None:
        return candidates[:top_k]

    pairs = [[query, doc] for doc in candidates]
    rerank_scores = _reranker.predict(pairs)
    ranked = [doc for _, doc in sorted(zip(rerank_scores, candidates), reverse=True)]
    return ranked[:top_k]
