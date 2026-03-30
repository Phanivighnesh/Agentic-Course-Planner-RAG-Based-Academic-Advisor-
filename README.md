# Agentic-Course-Planner-RAG-Based-Academic-Advisor-

Agentic Course Planner system built with **CrewAI**, **LangChain**, **FAISS**, **Groq (llama-3.1-8b-instant)**, and **HuggingFace Embeddings** that helps students plan courses strictly grounded in academic catalog documents.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI  (app.py)                  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                  CrewAI Sequential Crew                     │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Intake Agent │→ │ Retriever    │→ │  Planner Agent   │   │
│  │              │  │ Agent        │  │                  │   │
│  │ Collects &   │  │ Fetches      │  │ Builds term plan │   │
│  │ normalises   │  │ grounded     │  │ with citations   │   │
│  │ student info │  │ catalog text │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                              │              │
│                              ┌───────────────▼────────────┐ │
│                              │  Verifier / Auditor Agent  │ │
│                              │ Checks citations & prereqs │ │
│                              └────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    RAG Pipeline                             │
│  TXT/HTML/PDF → Chunking (500t/100 overlap) →               │
│  all-MiniLM-L6-v2 (HuggingFace, local) → FAISS index        │
└─────────────────────────────────────────────────────────────┘
                            │
              Groq API  ·  llama-3.1-8b-instant
```

---

## 📋 Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com/keys)
- 4GB RAM (embeddings run locally; LLM calls go to Groq cloud)

No GPU required. No Ollama required.

---

## ⚡ Setup

### 1. Clone & install

```bash
git clone <your-repo-url>
cd rag_advisor
pip install -r requirements.txt
```

### 2. Add your Groq API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free key at: **https://console.groq.com/keys**

### 3. Add catalog documents

Place catalog `.txt` / `.html` / `.pdf` files in `data/catalog/`.  
See `data/catalog/README.md` for sourcing instructions.

The repo ships with two real Georgia Tech catalog files ready to use:
- `gatech_cs_catalog.txt` — CS courses, degree requirements, academic policies
- `gatech_threads_requirements.txt` — Thread requirements and 4-year plan

### 4. Build the vector index

```bash
python -m rag.ingest
```

Downloads `all-MiniLM-L6-v2` (~90MB, one time) and builds the FAISS index.

### 5. Launch the Streamlit app

```bash
streamlit run app.py
```

Opens at **http://localhost:8501**

---

## 🧪 Running the Evaluation Suite

```bash
# Quick smoke test (first 3 queries only):
python evaluation/run_eval.py --limit 3

# Full 25-query evaluation with saved report:
python evaluation/run_eval.py --output eval_results.json
```

Each query has a 120-second timeout. Results are saved after every query
so you don't lose progress if it's interrupted.

---

## 🔧 Running the Smoke Test

```bash
python quick_start.py
```

Verifies index build → retriever → one full crew run end-to-end.

---

## 📁 Project Structure

```
rag_advisor/
├── app.py                        # Streamlit UI
├── quick_start.py                # End-to-end smoke test
├── requirements.txt
├── .env                          # GROQ_API_KEY (you create this)
├── config/
│   └── settings.py               # Central config (models, paths, chunk sizes)
├── rag/
│   ├── ingest.py                 # Document loading, chunking, FAISS
│   ├── retriever.py              # Retriever with citation metadata
│   └── prompts.py                # All agent prompts
├── agents/
│   └── crew.py                   # CrewAI 4-agent orchestration
├── utils/
│   ├── formatting.py             # Output parser + Streamlit renderer
│   └── session.py                # Session state management
├── evaluation/
│   ├── test_queries.py           # 25-query test set
│   ├── run_eval.py               # Evaluation runner
│   └── results_schema.json       # JSON schema for eval output
└── data/
    ├── catalog/                  # Catalog documents (add yours here)
    │   ├── gatech_cs_catalog.txt
    │   └── gatech_threads_requirements.txt
    └── faiss_index/              # Auto-generated after ingestion
```

---

## 🔑 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | CrewAI | Native multi-agent orchestration with sequential task flow |
| LLM | Groq · llama-3.1-8b-instant | ~750 tokens/sec, free tier, no local GPU needed |
| Embeddings | all-MiniLM-L6-v2 (HuggingFace) | Lightweight local embeddings (~90MB), no API cost |
| Vector Store | FAISS | In-memory, no infrastructure overhead |
| Chunk size | 500 tokens / 100 overlap | Captures one full course description without splitting |
| Retriever k | 6 chunks | Covers multi-hop prerequisite chains (A→B→C) |
| Temperature | 0.1 | Near-deterministic for factual grounding |

---

## 📊 Catalog Sources

| File | URL | Accessed | Covers |
|------|-----|----------|--------|
| gatech_cs_catalog.txt | https://catalog.gatech.edu/courses-undergrad/cs/ | 2025-03-29 | CS 1301–CS 4803, degree requirements, academic policies |
| gatech_threads_requirements.txt | https://catalog.gatech.edu/programs/computer-science-bs/ | 2025-03-29 | Thread requirements, 4-year plan |

---

## ⚠️ Known Limitations & Next Improvements

- Course availability per semester is not in catalogs → system correctly abstains
- Multi-hop chains (4+ hops) can occasionally have reasoning errors → caught by Verifier agent
- **Next:** Add cross-encoder re-ranking for higher precision retrieval
- **Next:** Persistent conversation memory across Streamlit sessions (SQLite)
- **Next:** Hybrid BM25 + dense retrieval for exact course code lookups
