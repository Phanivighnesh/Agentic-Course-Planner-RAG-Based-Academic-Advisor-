
"""
quick_start.py
Smoke-test script — verifies the full pipeline works end-to-end
without launching the Streamlit UI.

Usage:
    python quick_start.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


def main() -> None:
    console.rule("[bold blue]Agentic RAG — Quick Start Smoke Test[/bold blue]")

    # ── Step 1: Build index ───────────────────────────────────────────────────
    console.print("\n[bold]Step 1:[/bold] Building vector index from catalog…")
    try:
        from rag.ingest import run_ingestion
        run_ingestion()
        console.print("[green]✅ Index built successfully.[/green]")
    except Exception as e:
        console.print(f"[red]❌ Ingestion failed: {e}[/red]")
        console.print("[dim]Make sure GROQ_API_KEY is set in your .env file[/dim]")
        sys.exit(1)

    # ── Step 2: Test retriever ────────────────────────────────────────────────
    console.print("\n[bold]Step 2:[/bold] Testing retriever…")
    try:
        from rag.retriever import get_retriever
        retriever = get_retriever()
        chunks = retriever.query("What are the prerequisites for CS 310?")
        console.print(f"[green]✅ Retrieved {len(chunks)} chunks.[/green]")
        for c in chunks[:2]:
            console.print(Panel(c.content[:300] + "…", title=c.citation_string(), expand=False))
    except Exception as e:
        console.print(f"[red]❌ Retriever failed: {e}[/red]")
        sys.exit(1)

    # ── Step 3: Run one crew query ────────────────────────────────────────────
    console.print("\n[bold]Step 3:[/bold] Running one crew query (this may take 30–90s)…")
    try:
        from agents.crew import run_crew
        result = run_crew(
            student_message="Can I take CS 310 if I've completed CS 201 and CS 150?",
            profile={
                "completed_courses": ["CS 201", "CS 150"],
                "target_program": "B.S. Computer Science",
                "target_term": "Fall 2025",
                "max_credits": 18,
            },
        )
        console.print("[green]✅ Crew completed.[/green]")
        console.print(Panel(result[:1000] + ("…" if len(result) > 1000 else ""),
                            title="Agent Response (truncated)", expand=False))
    except Exception as e:
        console.print(f"[red]❌ Crew failed: {e}[/red]")
        console.print("[dim]Check that GROQ_API_KEY is set correctly in your .env file[/dim]")
        sys.exit(1)

    console.rule("[bold green]All checks passed! Run: streamlit run app.py[/bold green]")



if __name__ == "__main__":
    main()

