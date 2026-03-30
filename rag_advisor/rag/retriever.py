"""
rag/retriever.py
Retriever wrapper that returns chunks with full citation metadata.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    EMBED_MODEL,
    FAISS_INDEX_DIR,
    RETRIEVER_K,
)


@dataclass
class RetrievedChunk:
    """A retrieved catalog chunk with its provenance."""
    content:    str
    chunk_id:   str
    source_url: str = ""
    source_file: str = ""
    section:    str = ""
    score:      float = 0.0

    def citation_string(self) -> str:
        parts = []
        if self.source_url:
            parts.append(self.source_url)
        elif self.source_file:
            parts.append(self.source_file)
        if self.section:
            parts.append(f"§ {self.section}")
        parts.append(f"[{self.chunk_id}]")
        return " — ".join(parts)


class CatalogRetriever:
    """
    Thin wrapper around FAISS that returns RetrievedChunk objects.
    Loads the index lazily on first query.
    """

    def __init__(self, k: int = RETRIEVER_K):
        self.k           = k
        self._vectorstore: Optional[FAISS] = None

    def _load(self) -> FAISS:
        if self._vectorstore is None:
            embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
            self._vectorstore = FAISS.load_local(
                str(FAISS_INDEX_DIR),
                embeddings,
                allow_dangerous_deserialization=True,
            )
        return self._vectorstore

    def query(self, question: str) -> List[RetrievedChunk]:
        """Return the top-k most relevant catalog chunks for a question."""
        store = self._load()
        results = store.similarity_search_with_score(question, k=self.k)

        chunks: List[RetrievedChunk] = []
        for doc, score in results:
            m = doc.metadata
            chunks.append(
                RetrievedChunk(
                    content     = doc.page_content,
                    chunk_id    = m.get("chunk_id", "unknown"),
                    source_url  = m.get("source_url", ""),
                    source_file = m.get("source_file", ""),
                    section     = m.get("section", ""),
                    score       = float(score),
                )
            )
        return chunks

    def format_context(self, chunks: List[RetrievedChunk]) -> str:
        """Format chunks as a numbered context block for LLM prompts."""
        lines = []
        for i, c in enumerate(chunks, 1):
            lines.append(
                f"[CHUNK {i} | {c.citation_string()}]\n{c.content}\n"
            )
        return "\n---\n".join(lines)


# Singleton — shared across all agents
_retriever_instance: Optional[CatalogRetriever] = None


def get_retriever() -> CatalogRetriever:
    global _retriever_instance
    if _retriever_instance is None:
        _retriever_instance = CatalogRetriever()
    return _retriever_instance
