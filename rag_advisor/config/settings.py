from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR        = Path(__file__).resolve().parent.parent
CATALOG_DIR     = BASE_DIR / "data" / "catalog"
FAISS_INDEX_DIR = BASE_DIR / "data" / "faiss_index"

# ── Groq ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY")
LLM_MODEL      = "llama-3.1-8b-instant"   # Groq model ID

# ── Embeddings (local HuggingFace — no Ollama needed) ─────────────────────────
EMBED_MODEL    = "sentence-transformers/all-MiniLM-L6-v2"

# ── Chunking ──────────────────────────────────────────────────────────────────
CHUNK_SIZE     = 500
CHUNK_OVERLAP  = 100

# ── Retrieval ─────────────────────────────────────────────────────────────────
RETRIEVER_K    = 6

# ── Agent LLM settings ────────────────────────────────────────────────────────
LLM_TEMPERATURE  = 0.1
LLM_MAX_TOKENS   = 2048

OUTPUT_SECTIONS = [
    "Answer / Plan",
    "Why (requirements/prereqs satisfied)",
    "Citations",
    "Clarifying Questions (if needed)",
    "Assumptions / Not in Catalog",
]






