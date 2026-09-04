"""
Shared theme styling for AIR-Bud.
ASU Color Scheme: Maroon (#8C1515), Gold (#FFB81C), White (#FFFFFF)
ASU uses Merriweather (headings) and Proxima Nova (body) — we approximate with web fonts.
"""
import streamlit as st

ASU_MAROON = "#8C1515"
ASU_GOLD = "#FFB81C"
ASU_WHITE = "#FFFFFF"
ASU_LIGHT = "#F6F6F6"
ASU_BORDER = "#E0E0E0"
ASU_TEXT = "#333333"
ASU_TEXT_LIGHT = "#6B6B6B"

_APP_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700;900&family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
    --maroon: {ASU_MAROON};
    --gold: {ASU_GOLD};
    --text: {ASU_TEXT};
    --text-light: {ASU_TEXT_LIGHT};
    --border: {ASU_BORDER};
    --light: {ASU_LIGHT};
}}

/* ─── Global Typography ─── */
body {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text) !important;
}}
h1, h2, h3, h4, h5, h6 {{
    font-family: 'Merriweather', Georgia, serif !important;
    color: var(--maroon) !important;
}}
p, span, label, div, a, li, td, th, input, textarea {{
    color: var(--text) !important;
}}

/* Remove Streamlit branding */
#MainMenu {{ display: none !important }}
footer {{ visibility: hidden }}
header {{ visibility: hidden }}

/* Main background */
.stApp {{
    background-color: var(--light);
}}

/* Hide Streamlit page nav */
.section-nav {{ display: none !important }}
[data-testid="stSidebarNav"] {{ display: none !important }}

/* ─── Sidebar: Clean white with maroon top bar ─── */
section[data-testid="stSidebar"] {{
    background: white !important;
    border-right: 1px solid var(--border) !important;
}}
section[data-testid="stSidebar"] * {{
    color: var(--text) !important;
}}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{
    color: var(--maroon) !important;
}}
section[data-testid="stSidebar"] .stDivider {{
    border-color: var(--border) !important;
}}
section[data-testid="stSidebar"] .stExpander .streamlit-expanderHeader {{
    background: var(--light);
    border-radius: 6px;
    border: 1px solid var(--border);
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem;
}}
section[data-testid="stSidebar"] .stExpander div[role="document"] {{
    background: white;
    border-radius: 6px;
}}

/* Sidebar brand */
.sidebar-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 1rem 0.75rem 0.75rem;
    margin-bottom: 0.25rem;
}}
.sidebar-brand-text {{
    font-family: 'Merriweather', serif;
    font-size: 1.3rem;
    font-weight: 900;
    color: var(--maroon) !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
}}
.sidebar-brand-sub {{
    font-family: 'Inter', sans-serif;
    font-size: 0.68rem;
    color: var(--text-light) !important;
    margin: 0 !important;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}

/* Nav links */
.nav-link {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 14px;
    margin: 1px 8px;
    border-radius: 6px;
    color: var(--text) !important;
    text-decoration: none !important;
    font-family: 'Inter', sans-serif;
    font-size: 0.84rem;
    font-weight: 500;
    transition: all 0.12s ease;
    cursor: pointer;
    border-left: 3px solid transparent;
}}
.nav-link:hover {{
    background: var(--light) !important;
    border-left-color: var(--gold);
}}
.nav-link.active {{
    background: rgba(140,21,21,0.05) !important;
    color: var(--maroon) !important;
    font-weight: 600;
    border-left-color: var(--maroon);
}}
.nav-icon {{
    font-size: 1.05rem;
    width: 22px;
    text-align: center;
}}

/* ─── Buttons ─── */
.stButton > button {{
    background-color: var(--maroon) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.2rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    box-shadow: 0 1px 3px rgba(140,21,21,0.15) !important;
    transition: all 0.15s ease !important;
}}
.stButton > button:hover {{
    background-color: #6B0F0F !important;
    transform: translateY(-1px);
}}

/* ─── Cards & Panels ─── */
.feature-card {{
    background: white;
    border-radius: 10px;
    padding: 1.2rem;
    margin: 0.35rem 0;
    border: 1px solid var(--border);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
    height: 100%;
    display: flex;
    flex-direction: column;
}}
.feature-card:hover {{
    border-color: var(--gold);
    box-shadow: 0 3px 12px rgba(255,184,28,0.1);
    transform: translateY(-1px);
}}

.panel {{
    background: white;
    border-radius: 10px;
    border: 1px solid var(--border);
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    padding: 1.25rem;
    height: 100%;
    box-sizing: border-box;
}}
.panel-header {{
    font-family: 'Merriweather', serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--maroon);
    margin: 0 0 1rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid var(--maroon);
}}
.panel-section {{
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 1rem 0 0.5rem;
}}

/* Calendar */
.calendar-grid {{
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 2px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
}}
.calendar-header-cell {{
    text-align: center;
    font-weight: 600;
    font-size: 0.68rem;
    color: var(--text-light);
    padding: 6px 0;
    text-transform: uppercase;
}}
.calendar-day {{
    text-align: center;
    padding: 6px 2px;
    border-radius: 6px;
    cursor: default;
    position: relative;
}}
.calendar-day.today {{
    background: var(--maroon);
    color: white;
    font-weight: 700;
}}
.calendar-day.has-event {{
    background: rgba(255,184,28,0.15);
    color: var(--maroon);
    font-weight: 600;
}}
.calendar-day.has-event::after {{
    content: '';
    display: block;
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: var(--gold);
    margin: 2px auto 0;
}}
.calendar-day.empty {{
    visibility: hidden;
}}

/* Event list */
.event-item {{
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 10px;
    margin: 4px 0;
    border-radius: 6px;
    border: 1px solid var(--border);
    background: var(--light);
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    transition: all 0.12s ease;
}}
.event-item:hover {{
    border-color: var(--gold);
    background: white;
}}
.event-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 4px;
    flex-shrink: 0;
}}

/* AI Chat */
.ai-chat-header {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.ai-status {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #22c55e;
    display: inline-block;
}}

/* Stat cards */
.stat-card-value {{
    font-family: 'Merriweather', serif;
    font-size: 1.3rem;
    font-weight: 900;
    color: var(--maroon);
    margin: 0;
}}
.stat-card-label {{
    font-family: 'Inter', sans-serif;
    font-size: 0.7rem;
    color: var(--text-light);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 4px 0 0;
}}

/* Typography */
.page-title {{
    font-family: 'Merriweather', serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: var(--maroon);
}}

/* Inputs */
.stTextInput > div > div > input {{
    border-radius: 6px;
    border: 1px solid var(--border);
    font-family: 'Inter', sans-serif;
    color: var(--text) !important;
}}
.stTextInput > div > div > input:focus {{
    border-color: var(--maroon);
    box-shadow: 0 0 0 2px rgba(140,21,21,0.1);
}}
.stSelectbox > div > div > div {{
    border-radius: 6px;
    border: 1px solid var(--border);
    font-family: 'Inter', sans-serif;
}}

/* Metric accent */
.stMetric > div {{
    border-left: 3px solid var(--gold);
    padding-left: 0.5rem;
}}

/* Dividers */
.stDivider {{
    border-color: var(--border) !important;
}}

/* Alerts */
.stAlert {{
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
}}

/* Chat messages */
.stChatMessage {{
    border-radius: 10px;
    border: 1px solid var(--border);
}}

/* Caption text */
caption, .stCaption {{
    color: var(--text-light) !important;
}}
</style>
"""


def apply_theme():
    """Apply shared ASU theme styling. Call once per page."""
    st.markdown(_APP_CSS, unsafe_allow_html=True)


def sidebar_brand():
    """Render the AIR-Bud sidebar brand."""
    st.markdown("""
    <div class="sidebar-brand">
        <div>
            <div class="sidebar-brand-text">🎓 AIR-Bud</div>
            <div class="sidebar-brand-sub">Am I Ready?</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def sidebar_nav(current_page: str = ""):
    """Render navigation links in the sidebar."""
    pages = [
        ("🏠", "Home", "app.py"),
        ("📄", "Upload Syllabus", "pages/01_Upload_Syllabus.py"),
        ("📅", "Timeline & Calendar", "pages/02_Timeline_Calendar.py"),
        ("🤖", "Study Companion", "pages/03_Study_Companion.py"),
        ("📝", "Notes & Assignments", "pages/04_Notes_Assignments.py"),
        ("❓", "Mock Quizzes", "pages/05_Mock_Quiz.py"),
        ("📊", "Readiness Check", "pages/06_Readiness_Assessment.py"),
        ("🗓️", "Study Plan", "pages/07_Study_Plan.py"),
    ]
    for icon, label, path in pages:
        active = " active" if path == current_page else ""
        st.markdown(
            f'<a href="{path}" class="nav-link{active}">'
            f'<span class="nav-icon">{icon}</span>{label}</a>',
            unsafe_allow_html=True,
        )


def page_header(title: str, subtitle: str = ""):
    """Render a consistent page header."""
    st.markdown(f'<p class="page-title">{title}</p>', unsafe_allow_html=True)
    if subtitle:
        st.caption(subtitle)
    st.divider()