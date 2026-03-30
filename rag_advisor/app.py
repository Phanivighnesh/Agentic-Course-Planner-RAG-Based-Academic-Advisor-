
"""
app.py
Streamlit UI — Agentic RAG Course Planning Assistant

Run:
    streamlit run app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.crew import run_crew
from config.settings import FAISS_INDEX_DIR, LLM_MODEL, EMBED_MODEL
from utils.formatting import (
    format_citations_html,
    parse_structured_output,
    render_verdict_badge,
)
from utils.session import (
    add_message,
    get_messages,
    get_profile,
    init_session,
    reset_session,
    update_profile,
)

def clean_text(text: str) -> str:
    return (
        text
        .replace("```", "")
        .replace("`", "")
        .replace("📎", "")
        .strip()
    )

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="📚 Agentic Course Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1f3c88;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .section-card {
        background: #f8f9fa;
        border-left: 4px solid #1f3c88;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 0.6rem 0;
        color: #000000;
    }
    .citation-block {
        background: #eef2ff;
        border-left: 4px solid #4f6ef7;
        padding: 0.7rem 1rem;
        border-radius: 0 6px 6px 0;
        font-family: monospace;
        font-size: 0.85rem;
        color: #000000;
    }
    .warning-block {
        background: #fff8e6;
        border-left: 4px solid #f0a500;
        padding: 0.7rem 1rem;
        border-radius: 0 6px 6px 0;
    }
    .pass-badge  { color: #1a7a2a; font-weight: 700; }
    .fail-badge  { color: #b22222; font-weight: 700; }
    .user-msg    { background: #e8f0fe; border-radius: 12px; padding: 10px 14px; margin: 6px 0; }
    .assist-msg  { background: #f1f3f4; border-radius: 12px; padding: 10px 14px; margin: 6px 0; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar: Student Profile ───────────────────────────────────────────────────

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🎓 Student Profile")
        st.caption("Fill in your details to get accurate planning.")

        profile = get_profile()

        program = st.text_input(
            "Target Program / Major",
            value=profile.get("target_program", ""),
            placeholder="e.g. B.S. Computer Science",
        )
        term = st.text_input(
            "Target Term",
            value=profile.get("target_term", ""),
            placeholder="e.g. Fall 2025",
        )
        catalog_year = st.text_input(
            "Catalog Year",
            value=profile.get("catalog_year", ""),
            placeholder="e.g. 2024-2025",
        )
        max_credits = st.number_input(
            "Max Credits This Term",
            min_value=1, max_value=24,
            value=int(profile.get("max_credits", 18)),
        )
        completed_raw = st.text_area(
            "Completed Courses (comma-separated)",
            value=", ".join(profile.get("completed_courses", [])),
            placeholder="CS101, MATH120, PHYS101",
            height=80,
        )
        grades_raw = st.text_area(
            "Grades (optional, format: CS101:B+, MATH120:A)",
            value=", ".join(f"{k}:{v}" for k, v in profile.get("grades", {}).items()),
            placeholder="CS101:B+, MATH120:A-",
            height=60,
        )
        transfer_raw = st.text_area(
            "Transfer Credits (optional)",
            value=", ".join(profile.get("transfer_credits", [])),
            placeholder="CS101 equiv. from Community College",
            height=60,
        )

        if st.button("💾 Save Profile", use_container_width=True):
            completed = [c.strip().upper() for c in completed_raw.split(",") if c.strip()]
            grades: dict = {}
            for pair in grades_raw.split(","):
                pair = pair.strip()
                if ":" in pair:
                    k, v = pair.split(":", 1)
                    grades[k.strip().upper()] = v.strip()
            transfers = [t.strip() for t in transfer_raw.split(",") if t.strip()]

            update_profile({
                "target_program":   program,
                "target_term":      term,
                "catalog_year":     catalog_year,
                "max_credits":      max_credits,
                "completed_courses": completed,
                "grades":           grades,
                "transfer_credits": transfers,
            })
            st.success("Profile saved!")

        st.divider()

        # ── Index status
        st.markdown("## ⚙️ System")
        index_exists = FAISS_INDEX_DIR.exists() and any(FAISS_INDEX_DIR.iterdir())
        if index_exists:
            st.success("✅ Vector index loaded")
        else:
            st.warning("⚠️ No index found")
            if st.button("🔨 Build Index Now", use_container_width=True):
                with st.spinner("Ingesting catalog documents…"):
                    try:
                        from rag.ingest import run_ingestion
                        run_ingestion()
                        st.session_state.index_built = True
                        st.success("Index built successfully!")
                        st.rerun()
                    except FileNotFoundError as e:
                        st.error(str(e))

        st.caption(f"LLM: `{LLM_MODEL}` (Groq) | Embeddings: `all-MiniLM-L6-v2` (local)")
        st.divider()

        if st.button("🗑️ Clear Chat", use_container_width=True):
            reset_session()
            st.rerun()

        # ── Profile preview
        with st.expander("View current profile JSON"):
            st.json(get_profile())


# ── Response renderer ─────────────────────────────────────────────────────────

def render_structured_response(raw: str) -> None:
    """Parse and render the agent's structured output in a beautiful layout."""
    sections = parse_structured_output(raw)

    if "raw" in sections:
        # Fallback: couldn't parse sections — just display raw
        st.markdown(raw)
        return

    # Answer / Plan
    if ans := sections.get("Answer / Plan"):
        st.markdown("#### 📋 Answer / Plan")
        st.write(clean_text(ans))
        # st.markdown(f'<div class="section-card">{ans}</div>', unsafe_allow_html=True)

    # Why / Reasoning
    if why := sections.get("Why (requirements/prereqs satisfied)"):
        with st.expander("📖 Reasoning & Prerequisite Check", expanded=True):
            # st.markdown(why)
            st.write(clean_text(why))

    # Citations
    if cites := sections.get("Citations"):
        st.markdown("#### 📎 Citations")
        # st.markdown(
        #     f'<div class="citation-block">{format_citations_html(cites)}</div>',
        #     unsafe_allow_html=True
        # )
        clean_cites = clean_text(cites).replace("*", "<br>•")
        st.markdown(
            f'<div class="citation-block">{clean_cites}</div>',
            unsafe_allow_html=True
        )

    # Clarifying Questions
    if cqs := sections.get("Clarifying Questions (if needed)"):
        if cqs.strip().lower() not in ("none", "n/a", ""):
            st.markdown("#### ❓ Clarifying Questions")
            st.info(cqs)

    # Assumptions
    if assumptions := sections.get("Assumptions / Not in Catalog"):
        if assumptions.strip().lower() not in ("none", "n/a", ""):
            st.markdown("#### ⚠️ Assumptions / Not in Catalog")
            # st.markdown(
            #     f'<div class="warning-block">{assumptions}</div>',
            #     unsafe_allow_html=True
            # )
            st.markdown(
                f'<div class="warning-block">{clean_text(assumptions)}</div>',
                unsafe_allow_html=True
            )


# ── Chat interface ─────────────────────────────────────────────────────────────

def render_chat() -> None:
    st.markdown('<div class="main-header">📚 Agentic Course Planner</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Powered by CrewAI · FAISS · Groq llama3 — '
        'All answers grounded in your catalog documents.</div>',
        unsafe_allow_html=True
    )

    # Display message history
    for msg in get_messages():
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🎓"):
                render_structured_response(msg["content"])

    # Input
    if prompt := st.chat_input(
        "Ask about prerequisites, course eligibility, or request a term plan…"
    ):
        # Check index exists
        if not (FAISS_INDEX_DIR.exists() and any(FAISS_INDEX_DIR.iterdir())):
            st.error(
                "⚠️ Vector index not found. Please add catalog files to `data/catalog/` "
                "and click **Build Index Now** in the sidebar."
            )
            return

        add_message("user", prompt)
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="🎓"):
            with st.spinner("🤖 Agents working… (Intake → Retriever → Planner → Verifier)"):
                try:
                    response = run_crew(
                        student_message=prompt,
                        profile=get_profile(),
                    )
                except Exception as exc:
                    response = (
                        f"**Answer / Plan:**\nAn error occurred: `{exc}`\n\n"
                        f"**Assumptions / Not in Catalog:**\n"
                        f"Please ensure Ollama is running (`ollama serve`) and the index is built."
                    )

            render_structured_response(response)
            add_message("assistant", response)


# ── Example queries panel ─────────────────────────────────────────────────────

def render_examples() -> None:
    with st.expander("💡 Example queries to try", expanded=False):
        examples = [
            "Can I take CS301 if I've completed CS101 and MATH120?",
            "What do I need before enrolling in Database Systems?",
            "Plan my next term — I've done CS101 and MATH101, aiming for B.S. CS, max 15 credits.",
            "What is the full prerequisite chain to reach CS450?",
            "Is CS150 a co-requisite or prerequisite for CS201?",
            "How many credits do I need to graduate?",
            "Is CS301 offered in Fall 2025?",  # should abstain
            "Who teaches CS450 next semester?",  # should abstain
        ]
        cols = st.columns(2)
        for i, ex in enumerate(examples):
            if cols[i % 2].button(ex, key=f"ex_{i}", use_container_width=True):
                # Inject into chat as if user typed it
                add_message("user", ex)
                st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    init_session()
    render_sidebar()

    col1, col2 = st.columns([3, 1])
    with col1:
        render_examples()
        render_chat()

    with col2:
        st.markdown("### 📊 Session Stats")
        msgs = get_messages()
        user_msgs = [m for m in msgs if m["role"] == "user"]
        st.metric("Queries asked", len(user_msgs))
        profile = get_profile()
        st.metric("Courses completed", len(profile.get("completed_courses", [])))
        if profile.get("target_program"):
            st.success(f"Program: {profile['target_program']}")
        if profile.get("target_term"):
            st.info(f"Term: {profile['target_term']}")

        st.divider()
        st.markdown("### 📌 How it works")
        st.markdown("""
1. **Intake Agent** collects your profile
2. **Retriever Agent** searches the catalog (FAISS + nomic-embed-text)
3. **Planner Agent** builds a cited plan
4. **Verifier Agent** audits for errors
        """)


if __name__ == "__main__":
    main()
