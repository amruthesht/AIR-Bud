"""
Storage - Compatibility module.
Most functionality moved to utils/auth.py for user-scoped encrypted storage.
This module provides simple wrappers for backward compatibility.
"""
from utils.auth import (
    save_user_state,
    load_user_state,
    save_user_file,
    get_user_files,
)


def save_syllabus_data(session_state, data: dict):
    """Save parsed syllabus data to session state."""
    session_state["syllabus_data"] = data


def load_syllabus_data(session_state) -> dict:
    """Load parsed syllabus data from session state."""
    return session_state.get("syllabus_data", {})


def get_uploaded_notes(session_state) -> list:
    """Get list of uploaded notes/assignments from session state."""
    return session_state.get("uploaded_notes", [])


def get_quiz_history(session_state) -> list:
    """Get quiz attempt history."""
    return session_state.get("quiz_history", [])


def get_study_plan(session_state) -> dict:
    """Get the current study plan."""
    return session_state.get("study_plan", {})


def get_readiness_assessment(session_state) -> dict:
    """Get the latest readiness assessment."""
    return session_state.get("readiness_assessment", {})
