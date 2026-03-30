"""
evaluation/test_queries.py
25-query evaluation test set covering all required categories.

Categories:
  - prereq_check   (10): eligible / not eligible decisions
  - chain_question  (5): multi-hop, needs 2+ pieces of evidence
  - program_req     (5): electives, credits, required categories
  - not_in_docs     (5): trick/abstention questions
"""

from typing import TypedDict, Literal

Category = Literal["prereq_check", "chain_question", "program_req", "not_in_docs"]


class TestQuery(TypedDict):
    id: str
    category: Category
    query: str
    profile: dict
    expected_decision: str          # "eligible" | "not_eligible" | "need_info" | "abstain"
    rubric_notes: str


TEST_QUERIES: list[TestQuery] = [

    # ── 10 Prerequisite Checks ────────────────────────────────────────────────

    {
        "id": "PQ01",
        "category": "prereq_check",
        "query": "Can I take CS301 if I've completed CS101 and MATH120?",
        "profile": {
            "completed_courses": ["CS101", "MATH120"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "CS301 typically requires CS101. Should cite prereq rule.",
    },
    {
        "id": "PQ02",
        "category": "prereq_check",
        "query": "Am I eligible for Database Systems (CS450) with only CS101 done?",
        "profile": {
            "completed_courses": ["CS101"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "not_eligible",
        "rubric_notes": "CS450 typically requires CS301 or equivalent. Missing CS301.",
    },
    {
        "id": "PQ03",
        "category": "prereq_check",
        "query": "Can I enroll in MATH301 (Calculus III) having taken MATH101 and MATH201?",
        "profile": {
            "completed_courses": ["MATH101", "MATH201"],
            "target_program": "B.S. Mathematics",
            "target_term": "Spring 2026",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Calculus III prereq is Calculus II (MATH201).",
    },
    {
        "id": "PQ04",
        "category": "prereq_check",
        "query": "I've taken CS101 with a D grade. Can I proceed to CS201?",
        "profile": {
            "completed_courses": ["CS101"],
            "grades": {"CS101": "D"},
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "not_eligible",
        "rubric_notes": "Many programs require C or better as prereq. Should cite minimum grade policy.",
    },
    {
        "id": "PQ05",
        "category": "prereq_check",
        "query": "Is CS150 a co-requisite or prerequisite for CS201?",
        "profile": {
            "completed_courses": ["CS101"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "need_info",
        "rubric_notes": "Requires finding co-req vs prereq distinction in catalog.",
    },
    {
        "id": "PQ06",
        "category": "prereq_check",
        "query": "Can I take CS499 (Senior Capstone) with 90 credits and CS301 completed?",
        "profile": {
            "completed_courses": ["CS101", "CS201", "CS301"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
            "credits_earned": 90,
        },
        "expected_decision": "eligible",
        "rubric_notes": "Capstone prereqs typically: senior standing + core courses.",
    },
    {
        "id": "PQ07",
        "category": "prereq_check",
        "query": "Do I need instructor consent to take an independent study course?",
        "profile": {
            "completed_courses": ["CS101", "CS201"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "need_info",
        "rubric_notes": "Instructor consent is an exception in the catalog — should be cited exactly.",
    },
    {
        "id": "PQ08",
        "category": "prereq_check",
        "query": "I completed CS201 and MATH120. Can I take CS310 (Algorithms)?",
        "profile": {
            "completed_courses": ["CS201", "MATH120"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Algorithms typically requires data structures + discrete math.",
    },
    {
        "id": "PQ09",
        "category": "prereq_check",
        "query": "Can I take PHYS201 (Physics II) having only taken PHYS101?",
        "profile": {
            "completed_courses": ["PHYS101"],
            "target_program": "B.S. Computer Science",
            "target_term": "Spring 2026",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Physics II prereq is Physics I in most catalogs.",
    },
    {
        "id": "PQ10",
        "category": "prereq_check",
        "query": "I have transfer credit for CS101 equivalent. Can I take CS201?",
        "profile": {
            "completed_courses": [],
            "transfer_credits": ["CS101 equivalent from Community College"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "need_info",
        "rubric_notes": "Transfer credit acceptance policy must be cited; may need advisor confirmation.",
    },

    # ── 5 Prerequisite Chain Questions (multi-hop) ────────────────────────────

    {
        "id": "CQ01",
        "category": "chain_question",
        "query": "What is the full prerequisite chain I need to complete before taking CS450 (Database Systems)?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2026",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Should trace CS101→CS201→CS301→CS450 chain with citations at each hop.",
    },
    {
        "id": "CQ02",
        "category": "chain_question",
        "query": "How many terms minimum to reach CS499 (Capstone) starting from zero CS courses?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "need_info",
        "rubric_notes": "Multi-hop: trace chain + count terms. Should cite prereq chain per hop.",
    },
    {
        "id": "CQ03",
        "category": "chain_question",
        "query": "What courses must I take before enrolling in CS410 (Operating Systems)?",
        "profile": {
            "completed_courses": ["CS101"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "not_eligible",
        "rubric_notes": "OS typically requires CS201 + CS310. Missing both; multi-hop evidence needed.",
    },
    {
        "id": "CQ04",
        "category": "chain_question",
        "query": "I want to take Advanced Machine Learning. What's the full path from scratch?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2027",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Chain: CS101→CS201→MATH201→STAT301→CS460. Should cite 2+ hops.",
    },
    {
        "id": "CQ05",
        "category": "chain_question",
        "query": "Can I take both CS310 and CS410 next semester if I've completed CS201 and MATH120?",
        "profile": {
            "completed_courses": ["CS201", "MATH120"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "not_eligible",
        "rubric_notes": "CS310 might be eligible; CS410 probably not. Needs separate chain analysis.",
    },

    # ── 5 Program Requirement Questions ───────────────────────────────────────

    {
        "id": "PR01",
        "category": "program_req",
        "query": "How many total credits do I need to graduate with a B.S. in Computer Science?",
        "profile": {
            "completed_courses": ["CS101"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Must cite credit requirement from degree requirements page.",
    },
    {
        "id": "PR02",
        "category": "program_req",
        "query": "How many elective credits do I need and can any CS course count?",
        "profile": {
            "completed_courses": ["CS101", "CS201"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Should distinguish required electives vs free electives with citation.",
    },
    {
        "id": "PR03",
        "category": "program_req",
        "query": "What is the residency requirement — how many credits must be taken at the home institution?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Residency rule is in academic policy page. Must cite.",
    },
    {
        "id": "PR04",
        "category": "program_req",
        "query": "Can I repeat a course I failed to replace the grade in my GPA?",
        "profile": {
            "completed_courses": ["CS101"],
            "grades": {"CS101": "F"},
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Academic repeat/grade replacement policy. Must cite policy page.",
    },
    {
        "id": "PR05",
        "category": "program_req",
        "query": "What categories of courses are required in the CS core curriculum?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "eligible",
        "rubric_notes": "Should list required categories (theory, systems, etc.) from program page.",
    },

    # ── 5 Not-in-Docs / Trick Questions (Abstention) ──────────────────────────

    {
        "id": "ND01",
        "category": "not_in_docs",
        "query": "Is CS301 offered in Fall 2025 or only in Spring?",
        "profile": {
            "completed_courses": ["CS201"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "abstain",
        "rubric_notes": "Course availability by term is NOT in catalogs. Must abstain and redirect to schedule of classes.",
    },
    {
        "id": "ND02",
        "category": "not_in_docs",
        "query": "Who is the professor teaching CS450 next semester?",
        "profile": {
            "completed_courses": ["CS301"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "abstain",
        "rubric_notes": "Professor assignments not in catalog. Must abstain.",
    },
    {
        "id": "ND03",
        "category": "not_in_docs",
        "query": "What is the tuition cost per credit hour for CS courses?",
        "profile": {
            "completed_courses": [],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "abstain",
        "rubric_notes": "Tuition not in academic catalog. Must abstain and redirect.",
    },
    {
        "id": "ND04",
        "category": "not_in_docs",
        "query": "Can Professor Smith approve me for CS499 without completing CS401?",
        "profile": {
            "completed_courses": ["CS301"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "abstain",
        "rubric_notes": "Instructor consent details (specific professor policy) not in catalog. Partial abstain + cite instructor consent exception.",
    },
    {
        "id": "ND05",
        "category": "not_in_docs",
        "query": "Is there a waitlist for CS310 and how do I get on it?",
        "profile": {
            "completed_courses": ["CS201"],
            "target_program": "B.S. Computer Science",
            "target_term": "Fall 2025",
        },
        "expected_decision": "abstain",
        "rubric_notes": "Waitlist procedures not in academic catalog. Must abstain and redirect to registrar.",
    },
]
