"""
evaluation/run_eval.py
Evaluation runner for the 25-query test set.

Metrics:
  - Citation coverage rate
  - Eligibility correctness (prereq_check + chain_question)
  - Abstention accuracy (not_in_docs)

Usage:
    python evaluation/run_eval.py
    python evaluation/run_eval.py --output eval_results.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agents.crew import run_crew
from evaluation.test_queries import TEST_QUERIES

console = Console()


# ── Scoring helpers ───────────────────────────────────────────────────────────

def has_citations(response: str) -> bool:
    """Check if response contains at least one citation marker."""
    return bool(
        re.search(r"\[SOURCE:", response)
        or re.search(r"\[chunk_\d{4}\]", response)
        or re.search(r"\[CHUNK \d+", response)
    )


def detect_abstention(response: str) -> bool:
    """Check if response correctly abstains."""
    abstain_phrases = [
        "i don't have that information",
        "not in the provided catalog",
        "not in the catalog",
        "cannot find this information",
        "this information is not available",
        "i do not have",
        "not available in the",
    ]
    lower = response.lower()
    return any(phrase in lower for phrase in abstain_phrases)


def detect_eligibility(response: str) -> str:
    """
    Heuristically extract eligibility decision from response.
    Returns: "eligible" | "not_eligible" | "need_info" | "abstain" | "unknown"
    """
    lower = response.lower()

    if detect_abstention(response):
        return "abstain"

    not_eligible_signals = [
        "not eligible", "not yet eligible", "cannot enroll", "missing prerequisite",
        "does not meet", "have not completed", "need to complete first",
        "ineligible", "not qualified",
    ]
    eligible_signals = [
        "eligible to enroll", "you are eligible", "you can take", "you may enroll",
        "prerequisites are satisfied", "prerequisites met", "you qualify",
        "you have met", "cleared to enroll",
    ]
    need_info_signals = [
        "need more information", "clarifying question", "please provide",
        "could you confirm", "what grade", "which catalog year",
    ]

    if any(s in lower for s in not_eligible_signals):
        return "not_eligible"
    if any(s in lower for s in eligible_signals):
        return "eligible"
    if any(s in lower for s in need_info_signals):
        return "need_info"
    return "unknown"


# ── Single query runner ───────────────────────────────────────────────────────

def run_single(query_obj: Dict[str, Any]) -> Dict[str, Any]:
    qid      = query_obj["id"]
    query    = query_obj["query"]
    profile  = query_obj.get("profile", {})
    expected = query_obj["expected_decision"]
    category = query_obj["category"]

    console.print(f"\n[bold cyan]── {qid} ({category}) ──[/bold cyan]")
    console.print(f"[dim]{query}[/dim]")

    t0 = time.time()
    try:
        response = run_crew(student_message=query, profile=profile)
        elapsed  = time.time() - t0
        error    = None
    except Exception as exc:
        response = f"ERROR: {exc}"
        elapsed  = time.time() - t0
        error    = str(exc)
        console.print(f"[red]  ⚠  Exception: {exc}[/red]")

    cited       = has_citations(response)
    abstained   = detect_abstention(response)
    decision    = detect_eligibility(response)

    # Correctness scoring
    correct: bool | None = None
    if category in ("prereq_check", "chain_question"):
        correct = decision == expected
    elif category == "not_in_docs":
        correct = abstained
    elif category == "program_req":
        correct = cited  # for program reqs: citation coverage is the primary signal

    console.print(
        f"  Decision: [yellow]{decision}[/yellow] "
        f"| Expected: [green]{expected}[/green] "
        f"| Cited: {'✅' if cited else '❌'} "
        f"| Correct: {'✅' if correct else '❌' if correct is False else '⚪'} "
        f"| {elapsed:.1f}s"
    )

    return {
        "id":           qid,
        "category":     category,
        "query":        query,
        "expected":     expected,
        "decision":     decision,
        "cited":        cited,
        "abstained":    abstained,
        "correct":      correct,
        "elapsed_s":    round(elapsed, 2),
        "error":        error,
        "response":     response,
    }


# ── Report builder ────────────────────────────────────────────────────────────

def compute_metrics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(results)
    cited_count = sum(1 for r in results if r["cited"])

    prereq_results = [r for r in results if r["category"] in ("prereq_check", "chain_question")]
    prereq_correct = sum(1 for r in prereq_results if r["correct"])

    abstain_results = [r for r in results if r["category"] == "not_in_docs"]
    abstain_correct = sum(1 for r in abstain_results if r["correct"])

    return {
        "total_queries":          total,
        "citation_coverage_rate": round(cited_count / total * 100, 1),
        "eligibility_correct":    prereq_correct,
        "eligibility_total":      len(prereq_results),
        "eligibility_accuracy":   round(prereq_correct / max(len(prereq_results), 1) * 100, 1),
        "abstention_correct":     abstain_correct,
        "abstention_total":       len(abstain_results),
        "abstention_accuracy":    round(abstain_correct / max(len(abstain_results), 1) * 100, 1),
        "errors":                 sum(1 for r in results if r["error"]),
    }


def print_summary_table(metrics: Dict[str, Any]) -> None:
    table = Table(title="📊 Evaluation Summary", show_header=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")

    table.add_row("Total queries",          str(metrics["total_queries"]))
    table.add_row("Citation coverage",      f"{metrics['citation_coverage_rate']}%")
    table.add_row(
        "Eligibility accuracy",
        f"{metrics['eligibility_correct']}/{metrics['eligibility_total']} "
        f"({metrics['eligibility_accuracy']}%)"
    )
    table.add_row(
        "Abstention accuracy",
        f"{metrics['abstention_correct']}/{metrics['abstention_total']} "
        f"({metrics['abstention_accuracy']}%)"
    )
    table.add_row("Errors",                 str(metrics["errors"]))

    console.print(table)


# ── Main ──────────────────────────────────────────────────────────────────────

def main(output_path: str | None = None, limit: int | None = None) -> None:
    queries = TEST_QUERIES if limit is None else TEST_QUERIES[:limit]

    console.rule("[bold]Agentic RAG Evaluation Suite[/bold]")
    console.print(f"Running {len(queries)} queries …\n")

    results = [run_single(q) for q in queries]
    metrics = compute_metrics(results)

    console.rule("[bold]Results[/bold]")
    print_summary_table(metrics)

    report = {
        "$schema": "./evaluation/results_schema.json",
        "metrics": metrics,
        "results": results
    }

    if output_path:
        Path(output_path).write_text(json.dumps(report, indent=2))
        console.print(f"\n[dim]Full report saved → {output_path}[/dim]")
    else:
        console.print("\n[dim]Tip: add --output eval_results.json to save the full report.[/dim]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run RAG evaluation suite.")
    parser.add_argument("--output", type=str, default=None, help="Path to save JSON report.")
    parser.add_argument("--limit",  type=int, default=None, help="Run only first N queries (for testing).")
    args = parser.parse_args()
    main(output_path=args.output, limit=args.limit)
