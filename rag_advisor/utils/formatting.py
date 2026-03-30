"""
utils/formatting.py
Helpers to parse and render the structured agent output in Streamlit.
"""

from __future__ import annotations
import re
from typing import Dict


SECTION_KEYS = [
    "Answer / Plan",
    "Why (requirements/prereqs satisfied)",
    "Citations",
    "Clarifying Questions (if needed)",
    "Assumptions / Not in Catalog",
]


def parse_structured_output(raw: str) -> Dict[str, str]:
    """
    Parse the agent's mandatory structured output into a dict keyed by section.
    Falls back to {'raw': raw} if parsing fails.
    """
    sections: Dict[str, str] = {}

    # Build a pattern that splits on any of our section headers (bold markdown)
    pattern = r"\*\*(" + "|".join(re.escape(k) for k in SECTION_KEYS) + r"):\*\*"
    parts = re.split(pattern, raw)

    # parts = [preamble, header1, body1, header2, body2, ...]
    if len(parts) < 3:
        return {"raw": raw}

    i = 1
    while i < len(parts) - 1:
        header = parts[i].strip()
        body   = parts[i + 1].strip()
        sections[header] = body
        i += 2

    return sections if sections else {"raw": raw}


def render_verdict_badge(verified_output: str) -> str:
    """Return an emoji badge based on verifier verdict."""
    if "VERDICT: PASS" in verified_output:
        return "✅ PASS"
    elif "VERDICT: FAIL" in verified_output:
        return "❌ FAIL — see corrected plan below"
    return "⚠️ Unverified"


def format_citations_html(citations_text: str) -> str:
    """Wrap each citation line in a styled span for Streamlit markdown."""
    lines = citations_text.strip().splitlines()
    rendered = []
    for line in lines:
        line = line.strip()
        if line:
            rendered.append(f"📎 `{line}`")
    return "\n".join(rendered)
