"""
Shared theme styling for AIR-Bud.
ASU Color Scheme: Maroon (#8C1515), Gold (#FFB81C), White (#FFFFFF)
Import and call apply_theme() in each Streamlit page.
"""
import streamlit as st

ASU_MAROON = "#8C1515"
ASU_GOLD = "#FFB81C"
ASU_WHITE = "#FFFFFF"

_APP_CSS = f"""
<style>
    /* Override Streamlit primary button to ASU Maroon */
    .stButton > button {{
        background-color: {ASU_MAROON} !important;
        color: {ASU_WHITE} !important;
        border: none !important;
        border-radius: 8px !important;
    }}
    .stButton > button:hover {{
        background-color: #6B0F0F !important;
    }}

    /* Sidebar accent */
    section[data-testid="stSidebar"] {{
        border-right: 3px solid {ASU_MAROON} !important;
    }}

    /* Feature cards */
    .feature-card {{
        background: {ASU_WHITE};
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
        border-top: 4px solid {ASU_MAROON};
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
        height: 100%;
    }}
    .feature-card:hover {{
        border-top-color: {ASU_GOLD};
        box-shadow: 0 4px 12px rgba(255,184,28,0.2);
        transform: translateY(-2px);
    }}

    /* Headers */
    .page-title {{
        font-size: 2rem;
        font-weight: 700;
        color: {ASU_MAROON};
    }}
    .page-subtitle {{
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 1.5rem;
    }}

    /* Metric accent */
    .stMetric > div {{
        border-left: 3px solid {ASU_GOLD};
        padding-left: 0.5rem;
    }}
</style>
"""


def apply_theme():
    """Apply shared ASU theme styling. Call once per page."""
    st.markdown(_APP_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Render a consistent page header with ASU colors."""
    st.markdown(f'<p class="page-title">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
    st.divider()
