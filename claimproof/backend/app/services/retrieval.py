from typing import List
import chromadb
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

_chroma_client = chromadb.Client()
_collection = _chroma_client.get_or_create_collection(name="policy_clauses")

_stored_clauses: List[str] = []
_bm25_index = None

_reranker = CrossEncoder("BAAI/bge-reranker-base")


def index_policy_clauses(clauses: List[str]) -> None:
    """Stores tokenized policy clauses in both ChromaDB and BM25."""
    global _stored_clauses, _bm25_index
    _stored_clauses = clauses

    # Add to ChromaDB vector database
    if clauses:
        _collection.upsert(
            documents=clauses,
            ids=[f"clause_{i}" for i in range(len(clauses))],
        )
        # Build BM25 keyword index
        tokenized_corpus = [c.lower().split() for c in clauses]
        _bm25_index = BM25Okapi(tokenized_corpus)


def hybrid_retrieve(query: str, top_k: int = 3) -> List[str]:
    """
    Hybrid Retrieval:
    1. Semantic search via ChromaDB
    2. Keyword search via BM25
    3. Rerank combined results using BGE Reranker
    """
    if not _stored_clauses:
        return []

    vector_hits = _collection.query(query_texts=[query], n_results=min(top_k, len(_stored_clauses)))
    semantic_docs = vector_hits["documents"][0] if vector_hits.get("documents") else []

    keyword_docs = []
    if _bm25_index:
        scores = _bm25_index.get_scores(query.lower().split())
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        keyword_docs = [_stored_clauses[i] for i in top_indices]

    candidates = list(dict.fromkeys(semantic_docs + keyword_docs))
    if not candidates:
        return []

    pairs = [[query, doc] for doc in candidates]
    rerank_scores = _reranker.predict(pairs)
    ranked = [doc for _, doc in sorted(zip(rerank_scores, candidates), reverse=True)]

    return ranked[:top_k]