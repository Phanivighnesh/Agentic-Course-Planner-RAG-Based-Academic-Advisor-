# 🚀 Execution Guide — Agentic RAG Course Planning Assistant

Complete step-by-step instructions to set up and run the project from scratch on Windows.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have these installed:

| Tool | Version | Check Command | Download |
|------|---------|---------------|----------|
| Python | 3.10+ | `python --version` | https://python.org/downloads |
| pip | latest | `pip --version` | comes with Python |
| Git | any | `git --version` | https://git-scm.com |

> ⚠️ **Windows users:** During Python installation, check **"Add Python to PATH"** before clicking Install.

---

## PHASE 1 — Project Setup

### Step 1 — Get the project files

If you have the zip file downloaded, extract it to a folder of your choice.
You should see this structure after extracting:

```
rag_advisor/
├── app.py
├── requirements.txt
├── agents/
├── rag/
├── config/
├── evaluation/
├── utils/
└── data/
    └── catalog/
```

Open a terminal (Command Prompt or PowerShell on Windows) and navigate into the project:

```bash
cd path\to\rag_advisor
```

---

### Step 2 — Create a Virtual Environment

A virtual environment keeps this project's dependencies isolated from your system Python.
**Always do this — never install directly into system Python.**

```bash
# Create the virtual environment (named 'venv')
python -m venv venv
```

Now activate it:

```bash
# Windows Command Prompt
venv\Scripts\activate

# Windows PowerShell
venv\Scripts\Activate.ps1

# Mac / Linux
source venv/bin/activate
```

✅ You'll know it worked when your terminal prompt shows `(venv)` at the start:
```
(venv) C:\Users\YourName\rag_advisor>
```

> ⚠️ **PowerShell execution policy error?** Run this first:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

> ⚠️ **Always activate the venv before running ANY command in this project.**
> If you close the terminal and come back, re-run the activate command above.

---

### Step 3 — Install Dependencies

With the venv activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install all required packages including CrewAI, LangChain, FAISS,
Streamlit, Groq, and HuggingFace sentence-transformers.

> ⏳ First install takes 3–5 minutes. You'll see packages downloading.

Verify the install worked:

```bash
python -c "import crewai, langchain, faiss, streamlit; print('All good!')"
```

---

### Step 4 — Get Your Groq API Key

1. Go to **https://console.groq.com/keys**
2. Sign up for a free account (no credit card needed)
3. Click **"Create API Key"**
4. Copy the key (starts with `gsk_...`)

---

### Step 5 — Create the `.env` File

In your project root (`rag_advisor/`), create a file named exactly `.env` (no other extension):

```bash
# Windows Command Prompt
echo GROQ_API_KEY=your_key_here > .env

# Or create it manually in any text editor (Notepad, VS Code, PyCharm)
```

The file should contain exactly one line:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
```

> ⚠️ Never share this file or commit it to GitHub.
> Add `.env` to your `.gitignore` file.

---

## PHASE 2 — Catalog Data

### Step 6 — Add the Catalog Files

You should already have these two files from the catalog package:
- `gatech_cs_catalog.txt`
- `gatech_cs_catalog.meta.json`
- `gatech_threads_requirements.txt`
- `gatech_threads_requirements.meta.json`

Copy all four into `data/catalog/`:

```
rag_advisor/
└── data/
    └── catalog/
        ├── gatech_cs_catalog.txt          ← copy here
        ├── gatech_cs_catalog.meta.json    ← copy here
        ├── gatech_threads_requirements.txt     ← copy here
        └── gatech_threads_requirements.meta.json ← copy here
```

---

### Step 7 — Build the FAISS Vector Index

This reads all catalog files, chunks them, generates embeddings, and saves the index.

```bash
python -m rag.ingest
```

**What you'll see:**
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

> ⏳ **First run only:** Downloads the embedding model (~90MB). Takes 1–2 minutes.
> Subsequent runs are instant since the model is cached locally.

After this, you should see a new folder:
```
data/
└── faiss_index/
    ├── index.faiss
    └── index.pkl
```

> ⚠️ **If you add or change catalog files later**, always re-run this step:
> ```bash
> rmdir /s /q data\faiss_index
> python -m rag.ingest
> ```

---

## PHASE 3 — Running the Application

### Step 8 — Smoke Test (Optional but Recommended)

Run this before launching the UI to verify everything works end-to-end:

```bash
python quick_start.py
```

This tests: index loading → retriever → one full 4-agent crew run.

**Expected output:**
```
──────── Agentic RAG — Quick Start Smoke Test ────────
Step 1: Building vector index from catalog… ✅
Step 2: Testing retriever… ✅ Retrieved 6 chunks.
Step 3: Running one crew query (this may take 30–60s)…  ✅
──────── All checks passed! Run: streamlit run app.py ────────
```

> ⏳ Step 3 calls Groq API and runs 4 agents — takes 30–90 seconds normally.

---

### Step 9 — Launch the Streamlit App

```bash
streamlit run app.py
```

Your browser will open automatically at **http://localhost:8501**

If it doesn't open, manually go to that URL in your browser.

**Using the app:**

1. Fill in the **sidebar profile** on the left:
   - Target Program: `B.S. Computer Science`
   - Target Term: `Fall 2025`
   - Catalog Year: `2024-2025`
   - Max Credits: `15`
   - Completed Courses: e.g. `CS 1301, CS 1331`
   - Click **💾 Save Profile**

2. Type a question in the chat input at the bottom

3. Wait 30–60 seconds for the 4-agent pipeline to respond

To stop the app: press `Ctrl + C` in the terminal.

---

## PHASE 4 — Running the Evaluation

### Step 10 — Quick Evaluation Test (3 queries)

Always test with a small batch first:

```bash
python evaluation/run_eval.py --limit 3 --output eval_results.json
```

You'll see a live progress counter:
```
── [1/3] PQ01 (prereq_check) ──
Running... (max 120s)
✅ Decision: eligible | Expected: eligible | Cited: ✅ | 45.2s

── [2/3] PQ02 (prereq_check) ──
...
```

After all queries, a summary table prints:
```
         Evaluation Summary
┌────────────────────────────┬────────┐
│ Metric                     │ Value  │
├────────────────────────────┼────────┤
│ Total queries              │ 3      │
│ Citation coverage          │ 100%   │
│ Eligibility accuracy       │ 2/2    │
│ Abstention accuracy        │ 1/1    │
│ Errors                     │ 0      │
│ Timeouts                   │ 0      │
└────────────────────────────┴────────┘
```

---

### Step 11 — Full Evaluation (all 25 queries)

```bash
python evaluation/run_eval.py --output eval_results.json
```

> ⏳ Running all 25 queries takes approximately **20–40 minutes** total
> (each query = 4 agent LLM calls to Groq).
>
> Results are **saved after every query** to `eval_results.json` so
> you never lose progress even if the terminal is interrupted.

If a query times out (stuck for 120s), it's recorded as a timeout and
the runner **moves on automatically** — it will not hang forever.

---

## PHASE 5 — Troubleshooting

### ❌ `ModuleNotFoundError: No module named 'crewai'`
You're running Python outside the virtual environment.
```bash
# Re-activate first:
venv\Scripts\activate    # Windows
source venv/bin/activate # Mac/Linux

# Then retry your command
```

---

### ❌ `AuthenticationError: Invalid API Key`
Your Groq key is wrong or not loaded.
```bash
# Check your .env file exists and has the right content:
type .env          # Windows
cat .env           # Mac/Linux

# Should show:
# GROQ_API_KEY=gsk_xxxxxx
```

Make sure there are no extra spaces or quotes around the key.

---

### ❌ `FileNotFoundError: No supported catalog files found`
The catalog files are missing or in the wrong folder.
```bash
# Check what's in the catalog folder:
dir data\catalog      # Windows
ls data/catalog       # Mac/Linux
```
You need at least one `.txt`, `.html`, or `.pdf` file in there.

---

### ❌ `FAISS index not found` in the Streamlit UI
You haven't built the index yet, or it's in the wrong place.
```bash
python -m rag.ingest
```
After this, `data/faiss_index/` should exist with `index.faiss` and `index.pkl`.

---

### ❌ Evaluator stuck / not printing anything
The crew chain is hanging. It will auto-timeout at 120 seconds per query.
If you want to stop early:
- Press `Ctrl + C` in the terminal
- The partial `eval_results.json` file already has all results up to that point

To increase the timeout (e.g. slow internet):
Open `evaluation/run_eval.py` and change:
```python
QUERY_TIMEOUT = 120   # change to 180 or 240
```

---

### ❌ Groq `RateLimitError`
The free Groq tier has rate limits. If you hit them:
- Wait 60 seconds and retry
- Run `--limit 5` batches with breaks between them
- Check your usage at https://console.groq.com/usage

---

### ❌ PowerShell `cannot be loaded because running scripts is disabled`
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 📁 Complete Command Reference

```bash
# ── Setup ────────────────────────────────────────────────────────
python -m venv venv                          # create virtual environment
venv\Scripts\activate                        # activate (Windows CMD)
pip install -r requirements.txt              # install dependencies

# ── Every session (after closing terminal) ────────────────────────
venv\Scripts\activate                        # always activate first

# ── Catalog & Index ───────────────────────────────────────────────
python -m rag.ingest                         # build / rebuild vector index

# ── Testing ───────────────────────────────────────────────────────
python quick_start.py                        # smoke test (end-to-end check)

# ── App ───────────────────────────────────────────────────────────
streamlit run app.py                         # launch UI at localhost:8501

# ── Evaluation ────────────────────────────────────────────────────
python evaluation/run_eval.py --limit 3      # quick test (3 queries)
python evaluation/run_eval.py --output eval_results.json  # full 25 queries
```

---

