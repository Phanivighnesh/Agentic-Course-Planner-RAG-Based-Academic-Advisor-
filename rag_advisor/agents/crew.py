"""
agents/crew.py
CrewAI Crew definition — wires Intake, Retriever, Planner, and Verifier agents
into a sequential pipeline that produces a grounded, citation-verified response.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from crewai import Agent, Crew, Process, Task
from langchain_groq import ChatGroq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import LLM_MAX_TOKENS, LLM_MODEL, LLM_TEMPERATURE, GROQ_API_KEY
from rag.prompts import (
    INTAKE_SYSTEM,
    INTAKE_TASK,
    PLANNER_SYSTEM,
    PLANNER_TASK,
    RETRIEVER_SYSTEM,
    RETRIEVER_TASK,
    VERIFIER_SYSTEM,
    VERIFIER_TASK,
)
from rag.retriever import get_retriever


# ── LLM shared across all agents ─────────────────────────────────────────────

def _build_llm() -> ChatGroq:
    return ChatGroq(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
        api_key=GROQ_API_KEY,
    )

# ── Agent definitions ─────────────────────────────────────────────────────────

def make_intake_agent(llm: ChatGroq) -> Agent:
    return Agent(
        role="Student Intake Specialist",
        goal=(
            "Collect and normalise the student's academic profile. "
            "Identify any missing required fields and ask targeted clarifying questions. "
            "Produce a clean JSON profile before planning begins."
        ),
        backstory=(
            "You are a meticulous academic advisor's assistant who ensures all "
            "necessary student information is captured before any course planning occurs. "
            "You never proceed with incomplete information."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        system_prompt=INTAKE_SYSTEM,
    )


def make_retriever_agent(llm: ChatGroq) -> Agent:
    return Agent(
        role="Academic Catalog Retriever",
        goal=(
            "Retrieve and surface ONLY verbatim catalog text relevant to the student's "
            "courses and program requirements. Every fact must carry a chunk citation."
        ),
        backstory=(
            "You are an expert at reading dense academic catalogs and extracting "
            "precise prerequisite chains, co-requisites, and program rules. "
            "You never state anything that isn't directly quoted from the catalog."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        system_prompt=RETRIEVER_SYSTEM,
    )


def make_planner_agent(llm: ChatGroq) -> Agent:
    return Agent(
        role="Term Course Planner",
        goal=(
            "Produce a term course plan that is fully grounded in the catalog. "
            "Every course recommendation must include a citation proving eligibility. "
            "Flag any assumption or information not found in catalog documents."
        ),
        backstory=(
            "You are a senior academic advisor who has helped hundreds of students "
            "navigate complex prerequisite chains and degree requirements. "
            "You are meticulous about citing your sources and flagging uncertainty."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        system_prompt=PLANNER_SYSTEM,
    )


def make_verifier_agent(llm: ChatGroq) -> Agent:
    return Agent(
        role="Plan Auditor & Verifier",
        goal=(
            "Audit the planner's output for uncited claims, prerequisite errors, "
            "and hallucinated content. Issue a PASS or FAIL verdict with corrections."
        ),
        backstory=(
            "You are a quality-control specialist in academic planning systems. "
            "You have caught countless errors in AI-generated course plans and know "
            "exactly what grounding failures look like. You are ruthlessly thorough."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
        system_prompt=VERIFIER_SYSTEM,
    )


# ── Task builders ─────────────────────────────────────────────────────────────

def _make_tasks(
    agents: Dict[str, Agent],
    student_message: str,
    profile: Dict[str, Any],
    context: str,
    catalog_rules: str,
    plan_placeholder: str,
) -> list[Task]:

    profile_str   = json.dumps(profile, indent=2)
    target_term   = profile.get("target_term", "the next term")

    intake_task = Task(
        description=INTAKE_TASK.format(
            student_message=student_message,
            profile=profile_str,
        ),
        expected_output=(
            "A JSON block containing the normalised student profile, "
            "followed by any clarifying questions if fields are missing."
        ),
        agent=agents["intake"],
    )

    retriever_task = Task(
        description=RETRIEVER_TASK.format(
            profile=profile_str,
            question=student_message,
            context=context,
        ),
        expected_output=(
            "A structured list of all relevant catalog rules and prerequisites, "
            "each tagged with its chunk citation."
        ),
        agent=agents["retriever"],
        context=[intake_task],
    )

    planner_task = Task(
        description=PLANNER_TASK.format(
            profile=profile_str,
            catalog_rules=catalog_rules,
            target_term=target_term,
        ),
        expected_output=(
            "A complete structured term plan following the mandatory output format: "
            "Answer/Plan, Why, Citations, Clarifying Questions, Assumptions."
        ),
        agent=agents["planner"],
        context=[intake_task, retriever_task],
    )

    verifier_task = Task(
        description=VERIFIER_TASK.format(
            plan=plan_placeholder,
            context=context,
            profile=profile_str,
        ),
        expected_output=(
            "VERDICT: PASS or VERDICT: FAIL with specific issues and corrected plan."
        ),
        agent=agents["verifier"],
        context=[retriever_task, planner_task],
    )

    return [intake_task, retriever_task, planner_task, verifier_task]


# ── Main entry point ──────────────────────────────────────────────────────────

def run_crew(
    student_message: str,
    profile: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Orchestrate the full agent pipeline for a student query.

    Args:
        student_message: The raw student question or request.
        profile:         Known student profile dict (may be partial).

    Returns:
        Final verified response string.
    """
    if profile is None:
        profile = {}

    # ── RAG retrieval ────────────────────────────────────────────────────────
    retriever    = get_retriever()
    chunks       = retriever.query(student_message)
    context      = retriever.format_context(chunks)
    catalog_rules = context  # Planner sees the same context

    # ── Build agents ─────────────────────────────────────────────────────────
    llm = _build_llm()
    agents = {
        "intake":    make_intake_agent(llm),
        "retriever": make_retriever_agent(llm),
        "planner":   make_planner_agent(llm),
        "verifier":  make_verifier_agent(llm),
    }

    # ── Build tasks ───────────────────────────────────────────────────────────
    tasks = _make_tasks(
        agents          = agents,
        student_message = student_message,
        profile         = profile,
        context         = context,
        catalog_rules   = catalog_rules,
        plan_placeholder= "[Plan will be generated by Planner Agent]",
    )

    # ── Assemble & run crew ───────────────────────────────────────────────────
    crew = Crew(
        agents    = list(agents.values()),
        tasks     = tasks,
        process   = Process.sequential,
        verbose   = True,
        max_execution_time=60,
    )

    result = crew.kickoff()
    return str(result)
