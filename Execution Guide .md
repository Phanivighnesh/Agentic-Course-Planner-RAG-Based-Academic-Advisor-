# 🚀 Getting Started — Agentic Course Planner RAG Based Academic Advisor

A step-by-step guide for anyone cloning this repository and running it locally.

> **What this project does:** A multi-agent AI assistant that answers student course-planning
> questions strictly grounded in academic catalog documents — with citations, prerequisite
> reasoning, and safe abstention when information isn't in the catalog.

---

## 📋 Requirements

Make sure the following are installed before you begin:

| Tool | Minimum Version | How to check | Where to get it |
|------|----------------|--------------|-----------------|
| Python | 3.10+ | `python --version` | https://python.org/downloads |
| pip | latest | `pip --version` | comes with Python |
| Git | any | `git --version` | https://git-scm.com |

> ⚠️ **Windows:** During Python installation tick **"Add Python to PATH"** before clicking Install.

---

## STEP 1 — Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/rag_advisor.git](https://github.com/Phanivighnesh/Agentic-Course-Planner-RAG-Based-Academic-Advisor-.git)
cd rag_advisor
```

After cloning you should see this structure:

```
rag_advisor/
├── app.py
├── requirements.txt
├── quick_start.py
├── agents/
├── rag/
├── config/
├── evaluation/
├── utils/
└── data/
    └── catalog/
```

> **Three things that will NOT be present after cloning** — this is expected:
>
> | Missing item | Why | What to do |
> |-------------|-----|------------|
> | `.env` | Contains secret API key — never committed | Create it in Step 4 |
> | `data/faiss_index/` | Generated locally from your catalog files | Built in Step 6 |
> | Catalog `.txt` files (if excluded) | May be too large for repo | Add them in Step 5 |

---

## STEP 2 — Create a Virtual Environment

A virtual environment isolates this project's packages from the rest of your system.
**Always use one — never install directly into system Python.**

```bash
python -m venv venv
```

Activate it:

```bash
# Windows — Command Prompt
venv\Scripts\activate

# Windows — PowerShell
venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

Your terminal prompt will show `(venv)` when it's active:

```
(venv) C:\Users\YourName\rag_advisor>
```

> ⚠️ **PowerShell script error?**
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

> ⚠️ **Every time you open a new terminal**, re-run the activate command before
> running any project commands.

---

## STEP 3 — Install Dependencies

With the virtual environment active:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs CrewAI, LangChain, FAISS, Streamlit, Groq, HuggingFace
sentence-transformers, and all other required packages.

> ⏳ First install takes 3–5 minutes.

Verify everything installed correctly:

```bash
python -c "import crewai, langchain, faiss, streamlit; print('All packages OK')"
```

---

## STEP 4 — Get a Groq API Key and Create `.env`

This project uses **Groq** (free) to run `llama-3.1-8b-instant` as the LLM.
No GPU or local model download required.

**Get a free API key:**
1. Go to **https://console.groq.com/keys**
2. Sign up — no credit card needed
3. Click **"Create API Key"** and copy it (starts with `gsk_...`)

**Create a `.env` file** in the project root:

```bash
# Windows Command Prompt
echo GROQ_API_KEY=your_key_here > .env

# macOS / Linux
echo "GROQ_API_KEY=your_key_here" > .env
```

Or open any text editor and create `rag_advisor/.env` with this single line:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ `.env` is already listed in `.gitignore` so it will never be accidentally
> committed. Never share this file or post your key publicly.

---

## STEP 5 — Add Catalog Documents

The assistant needs academic catalog documents to answer questions from.
Place them in `data/catalog/`.

**This repo ships with two ready-to-use Georgia Tech catalog files:**

```
data/catalog/
├── gatech_cs_catalog.txt                  ✅ included
├── gatech_cs_catalog.meta.json            ✅ included
├── gatech_threads_requirements.txt        ✅ included
└── gatech_threads_requirements.meta.json  ✅ included
```

These cover CS courses CS 1301–CS 4803, degree requirements, thread
requirements, and academic policies — enough to run the full demo.

**Want to add your own university's catalog?**

Supported formats: `.txt`, `.html`, `.pdf`

Drop any catalog files into `data/catalog/` alongside a `.meta.json` sidecar:

```json
{
  "source_url": "https://catalog.youruni.edu/cs/courses",
  "accessed": "2025-03-29",
  "section": "CS Course Descriptions",
  "institution": "Your University",
  "catalog_year": "2024-2025"
}
```

The sidecar filename must match the catalog file — e.g. `my_catalog.txt` →
`my_catalog.meta.json`. This metadata appears in citations in the assistant's answers.

See `data/catalog/README.md` for more detail and wget/curl download examples.

---

## STEP 6 — Build the Vector Index

This reads all catalog files, splits them into chunks, generates embeddings,
and saves a FAISS index locally.

```bash
python -m rag.ingest
```

Expected output:

```
INFO  Loading  gatech_cs_catalog.txt
INFO  Loading  gatech_threads_requirements.txt
INFO  Loaded 2 raw document(s) from catalog.
INFO  Produced 47 chunks (size=500, overlap=100).
INFO  Initialising embedding model: sentence-transformers/all-MiniLM-L6-v2
INFO  Building FAISS index ...
INFO  Index saved → data/faiss_index/
✅  Ingestion complete.
```

> ⏳ **First run:** downloads the embedding model (~90MB). Takes 1–2 minutes.
> Every run after that is near-instant.

A new folder appears after this:

```
data/
└── faiss_index/
    ├── index.faiss
    └── index.pkl
```

> **Rebuilding the index** — run this any time you add or change catalog files:
> ```bash
> # Windows
> rmdir /s /q data\faiss_index
> python -m rag.ingest
>
> # macOS / Linux
> rm -rf data/faiss_index
> python -m rag.ingest
> ```

---

## STEP 7 — Verify Everything Works (Smoke Test optional this takes lot of time)

Run the smoke test before launching the UI — it checks the full pipeline
end-to-end in one command:

```bash
python quick_start.py
```

This runs three checks:

| Check | What it tests |
|-------|--------------|
| Step 1 | Index loads correctly |
| Step 2 | Retriever returns relevant chunks |
| Step 3 | Full 4-agent CrewAI pipeline completes one query |

Expected output:

```
──────── Agentic RAG — Quick Start Smoke Test ────────
Step 1: Building vector index from catalog… ✅
Step 2: Testing retriever… ✅ Retrieved 6 chunks.
Step 3: Running one crew query (this may take 30–60s)… ✅
──────── All checks passed! Run: streamlit run app.py ────────
```

> ⏳ Step 3 takes 30–90 seconds — it's calling the Groq API and running 4 agents.

---

## STEP 8 — Launch the App

```bash
streamlit run app.py
```

The browser opens automatically at **http://localhost:8501**

**How to use it:**

1. Fill in the **left sidebar** with the student profile:
   - Target Program → e.g. `B.S. Computer Science`
   - Target Term → e.g. `Fall 2025`
   - Catalog Year → `2024-2025`
   - Max Credits → `15`
   - Completed Courses → e.g. `CS 1301, CS 1331`
   - Click **💾 Save Profile**

2. Type a question in the chat box at the bottom, for example:
   - *"Can I take CS 3510 if I've completed CS 1332 and CS 2050?"*
   - *"Plan my next semester — I want to follow the Intelligence Thread."*
   - *"What is the full prerequisite chain to reach CS 4641?"*

3. Wait 30–60 seconds for the 4-agent pipeline to respond with a cited answer.

Press `Ctrl + C` in the terminal to stop the app.

---

## STEP 9 — Run the Evaluation Suite

The project includes a 25-query test set covering prerequisite checks,
multi-hop chains, program requirements, and abstention questions.

**Always run a quick test first:**

```bash
python evaluation/run_eval.py --limit 3 --output eval_results.json
```

**Full evaluation (all 25 queries):**

```bash
python evaluation/run_eval.py --output eval_results.json
```

> ⏳ Full run takes approximately 20–40 minutes (4 Groq API calls per query).
>
> Results are **saved after every single query** to `eval_results.json`
> so progress is never lost if interrupted.
>
> Each query has a **120-second timeout** — if a query hangs, it's logged
> as a timeout and the runner moves on automatically.

A summary table prints at the end:

```
           Evaluation Summary
┌──────────────────────────────┬──────────────┐
│ Metric                       │ Value        │
├──────────────────────────────┼──────────────┤
│ Total queries                │ 25           │
│ Citation coverage            │ 87%          │
│ Eligibility accuracy         │ 12/15 (80%)  │
│ Abstention accuracy          │ 9/10  (90%)  │
│ Errors                       │ 0            │
│ Timeouts                     │ 1            │
└──────────────────────────────┴──────────────┘
```

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'crewai'`
The virtual environment is not active.
```bash
venv\Scripts\activate    # Windows
source venv/bin/activate # macOS / Linux
```
Then re-run the command.

---

### ❌ `AuthenticationError` or `Invalid API Key`
```bash
type .env    # Windows — check the file content
cat .env     # macOS / Linux
```
The file must contain exactly: `GROQ_API_KEY=gsk_...` with no quotes or spaces.

---

### ❌ `FileNotFoundError: No supported catalog files found`
```bash
dir data\catalog    # Windows
ls data/catalog     # macOS / Linux
```
At least one `.txt`, `.html`, or `.pdf` file must be in `data/catalog/`.

---

### ❌ `FAISS index not found` error in the UI
Run ingestion first:
```bash
python -m rag.ingest
```

---

### ❌ Evaluator appears stuck / nothing printing
Each query auto-times out at 120 seconds. To increase the limit, open
`evaluation/run_eval.py` and change:
```python
QUERY_TIMEOUT = 120  # increase to 180 or 240
```
To stop early at any point: `Ctrl + C`. Partial results are already saved.

---

### ❌ Groq `RateLimitError`
The free Groq tier has per-minute limits. Wait 60 seconds and retry,
or run smaller batches with `--limit 5`. Monitor usage at https://console.groq.com/usage

---

### ❌ PowerShell activation error
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## ⚡ Quick Reference — All Commands

```bash
# ── Clone & setup (one time) ──────────────────────────────────────
git clone https://github.com/YOUR_USERNAME/rag_advisor.git
cd rag_advisor
python -m venv venv
venv\Scripts\activate                              # Windows
pip install -r requirements.txt
echo GROQ_API_KEY=gsk_xxxx > .env

# ── Every new terminal session ────────────────────────────────────
cd rag_advisor
venv\Scripts\activate

# ── Build / rebuild index ─────────────────────────────────────────
python -m rag.ingest

# ── Verify setup (optional)──────────────────────────────────────────────────
python quick_start.py

# ── Run the app ───────────────────────────────────────────────────
streamlit run app.py

# ── Run evaluation (optional)────────────────────────────────────────────────
python evaluation/run_eval.py --limit 3            # quick test
python evaluation/run_eval.py --output eval_results.json  # full run
```

---

## ✅ Setup Checklist

- [ ] Repository cloned and terminal is inside `rag_advisor/`
- [ ] Virtual environment created and active (`(venv)` in terminal prompt)
- [ ] `pip install -r requirements.txt` completed without errors
- [ ] `.env` created with a valid `GROQ_API_KEY`
- [ ] Catalog files present in `data/catalog/`
- [ ] `python -m rag.ingest` ran successfully
- [ ] `data/faiss_index/` folder exists with `index.faiss` and `index.pkl`
- [ ] `streamlit run app.py` — UI opens at localhost:8501

---

## 📂 Project Structure

```
rag_advisor/
├── app.py                          # Streamlit UI
├── quick_start.py                  # End-to-end smoke test
├── requirements.txt                # All Python dependencies
├── .env                            # Your Groq API key (create this, don't commit)
├── .gitignore                      # Excludes .env, venv/, faiss_index/
├── README.md                       # Project overview and architecture
├── WRITEUP.md                      # Assignment write-up
├── EXECUTION_GUIDE.md              # This file
│
├── config/
│   └── settings.py                 # Central config (models, chunk sizes, paths)
│
├── rag/
│   ├── ingest.py                   # Document loading → chunking → FAISS
│   ├── retriever.py                # FAISS retriever with citation metadata
│   └── prompts.py                  # All LLM prompts for every agent
│
├── agents/
│   └── crew.py                     # CrewAI 4-agent pipeline
│
├── utils/
│   ├── formatting.py               # Output parser + Streamlit renderer
│   └── session.py                  # Streamlit session state management
│
├── evaluation/
│   ├── test_queries.py             # 25-query test set
│   ├── run_eval.py                 # Evaluation runner with timeout + scoring
│   └── results_schema.json         # JSON schema for eval output
│
└── data/
    ├── catalog/                    # Put catalog documents here
    │   ├── gatech_cs_catalog.txt
    │   ├── gatech_threads_requirements.txt
    │   └── README.md
    └── faiss_index/                # Auto-generated — do not edit manually
```

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| Groq Console (API keys) | https://console.groq.com/keys |
| Groq Rate Limits | https://console.groq.com/docs/rate-limits |
| Georgia Tech Catalog | https://catalog.gatech.edu/courses-undergrad/cs/ |
| CrewAI Docs | https://docs.crewai.com |
| LangChain Docs | https://python.langchain.com |
| FAISS Docs | https://faiss.ai |
| Streamlit Docs | https://docs.streamlit.io |
