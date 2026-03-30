"""
utils/session.py
Streamlit session state helpers — profile persistence and chat history.
"""

from __future__ import annotations
import streamlit as st
from typing import Any, Dict, List


DEFAULT_PROFILE: Dict[str, Any] = {
    "completed_courses": [],
    "grades":            {},
    "target_program":    "",
    "catalog_year":      "",
    "target_term":       "",
    "max_credits":       18,
    "transfer_credits":  [],
}


def init_session() -> None:
    """Initialise session state defaults on first load."""
    if "messages" not in st.session_state:
        st.session_state.messages: List[Dict[str, str]] = []
    if "profile" not in st.session_state:
        st.session_state.profile: Dict[str, Any] = DEFAULT_PROFILE.copy()
    if "index_built" not in st.session_state:
        st.session_state.index_built: bool = False


def add_message(role: str, content: str) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def get_messages() -> List[Dict[str, str]]:
    return st.session_state.messages


def update_profile(updates: Dict[str, Any]) -> None:
    st.session_state.profile.update(updates)


def get_profile() -> Dict[str, Any]:
    return st.session_state.profile


def reset_session() -> None:
    st.session_state.messages = []
    st.session_state.profile  = DEFAULT_PROFILE.copy()
