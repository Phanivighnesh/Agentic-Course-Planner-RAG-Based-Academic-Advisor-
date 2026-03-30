"""
rag/ingest.py
Document ingestion pipeline:
  HTML / PDF / TXT  →  clean  →  chunk  →  embed  →  FAISS index

Run directly:
    python -m rag.ingest
"""

from __future__ import annotations

import json
import logging
import re
import sys
from pathlib import Path
from typing import List

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    BSHTMLLoader,
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    CATALOG_DIR,
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBED_MODEL,
    FAISS_INDEX_DIR,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)


# ── Cleaning ──────────────────────────────────────────────────────────────────

def _clean_text(text: str) -> str:
    """Normalise whitespace and strip boilerplate navigation artifacts."""
    text = re.sub(r"\s{3,}", "  ", text)          # collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)         # max 2 blank lines
    text = re.sub(r"[ \t]+\n", "\n", text)         # trailing spaces on lines
    text = re.sub(r"(Skip to|Jump to|Back to top).*?\n", "", text, flags=re.I)
    return text.strip()


# ── Loaders ───────────────────────────────────────────────────────────────────

def _load_html(path: Path) -> List[Document]:
    loader = BSHTMLLoader(str(path), open_encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.page_content = _clean_text(d.page_content)
        d.metadata["source_file"] = path.name
    return docs


def _load_pdf(path: Path) -> List[Document]:
    loader = PyPDFLoader(str(path))
    docs = loader.load()
    for d in docs:
        d.page_content = _clean_text(d.page_content)
        d.metadata["source_file"] = path.name
    return docs


def _load_txt(path: Path) -> List[Document]:
    loader = TextLoader(str(path), encoding="utf-8")
    docs = loader.load()
    for d in docs:
        d.page_content = _clean_text(d.page_content)
        d.metadata["source_file"] = path.name
    return docs


LOADER_MAP = {
    ".html": _load_html,
    ".htm":  _load_html,
    ".pdf":  _load_pdf,
    ".txt":  _load_txt,
}


def load_catalog(catalog_dir: Path = CATALOG_DIR) -> List[Document]:
    """Load every supported file from the catalog directory."""
    docs: List[Document] = []
    files = sorted(catalog_dir.rglob("*"))
    supported = [f for f in files if f.suffix.lower() in LOADER_MAP and f.is_file()]

    if not supported:
        raise FileNotFoundError(
            f"No supported catalog files found in {catalog_dir}.\n"
            "Add HTML/PDF/TXT files and re-run."
        )

    for path in supported:
        log.info("Loading  %s", path.name)
        try:
            loaded = LOADER_MAP[path.suffix.lower()](path)
            # Attach source URL from sidecar metadata if present
            meta_path = path.with_suffix(".meta.json")
            if meta_path.exists():
                meta = json.loads(meta_path.read_text())
                for d in loaded:
                    d.metadata.update(meta)
            docs.extend(loaded)
        except Exception as exc:
            log.warning("  ⚠  Could not load %s: %s", path.name, exc)

    log.info("Loaded %d raw document(s) from catalog.", len(docs))
    return docs


# ── Chunking ──────────────────────────────────────────────────────────────────

def chunk_documents(docs: List[Document]) -> List[Document]:
    """
    Split documents into overlapping chunks.

    Strategy:
    - RecursiveCharacterTextSplitter tries paragraph → sentence → word boundaries.
    - chunk_size=500 tokens keeps a full course description together.
    - chunk_overlap=100 prevents prerequisite text straddling two chunks silently.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Inject chunk index into metadata for citation tracing
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"chunk_{i:04d}"

    log.info("Produced %d chunks (size=%d, overlap=%d).", len(chunks), CHUNK_SIZE, CHUNK_OVERLAP)
    return chunks


# ── Embedding & Indexing ──────────────────────────────────────────────────────

def build_index(chunks: List[Document]) -> FAISS:
    """Embed chunks with nomic-embed-text and store in FAISS."""
    log.info("Initialising embedding model: %s", EMBED_MODEL)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    log.info("Building FAISS index …")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(FAISS_INDEX_DIR))
    log.info("Index saved → %s", FAISS_INDEX_DIR)
    return vectorstore


# ── Entry point ───────────────────────────────────────────────────────────────

def run_ingestion() -> FAISS:
    docs   = load_catalog()
    chunks = chunk_documents(docs)
    store  = build_index(chunks)
    return store


if __name__ == "__main__":
    run_ingestion()
    log.info("✅  Ingestion complete.")
