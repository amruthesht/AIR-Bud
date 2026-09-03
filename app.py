"""
AIR-Bud (Am I Ready) - AI Study/Syllabus Companion
Main Streamlit application entry point.
"""
import streamlit as st
import os
from pathlib import Path

st.set_page_config(
    page_title="AIR-Bud | Am I Ready?",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ASU Color scheme: Maroon #8C1515, Gold #FFB81C, White #FFFFFF
# Custom CSS
st.markdown("""
<style>
    /* Override Streamlit primary button to ASU Maroon */
    .stButton > button {
        background-color: #8C1515 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
    }
    .stButton > button:hover {
        background-color: #6B0F0F !important;
    }

    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: #8C1515;
        margin-bottom: 0.25rem;
    }
    .tagline {
        font-size: 1.3rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .feature-card {
        background: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
        border-top: 4px solid #8C1515;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        transition: all 0.2s ease;
        height: 100%;
    }
    .feature-card:hover {
        border-top-color: #FFB81C;
        box-shadow: 0 4px 12px rgba(255,184,28,0.2);
        transform: translateY(-2px);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }
    .onboarding-card {
        background: linear-gradient(135deg, #FFF8E7 0%, #FFFBF0 100%);
        border-radius: 20px;
        padding: 3rem;
        border: 2px solid #FFB81C;
        max-width: 500px;
        margin: 2rem auto;
    }
    .welcome-emoji {
        font-size: 4rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    /* Sidebar accent */
    section[data-testid="stSidebar"] {
        border-right: 3px solid #8C1515 !important;
    }
    /* Radio buttons */
    .stRadio > div {
        gap: 0.5rem;
    }
    /* Metric cards */
    .stMetric > div {
        border-left: 3px solid #FFB81C;
        padding-left: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Onboarding Check ─────────────────────────────────────────────────────
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

# If not logged in, show onboarding
if not st.session_state["user_logged_in"]:
    from utils.auth import create_user, login_user, list_users, load_user_state

    # Show mascot
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("assets/mascot-excited.png", width=180)

    with col2:
        st.markdown('<p class="main-title">AIR-Bud</p>', unsafe_allow_html=True)
        st.markdown('<p class="tagline">Am I Ready? Your AI Study Companion.</p>', unsafe_allow_html=True)

    tab_login, tab_signup = st.tabs(["🔑 Sign In", "✨ Create Account"])

    with tab_login:
        st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
        st.subheader("Welcome back!")

        login_user_input = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")

        if st.button("Sign In", type="primary", use_container_width=True, key="login_btn"):
            if login_user_input and login_pass:
                try:
                    profile = login_user(login_user_input, login_pass)
                    st.session_state["user_logged_in"] = True
                    st.session_state["current_user"] = profile
                    # Load user state
                    user_state = load_user_state(profile["username"])
                    for key, value in user_state.items():
                        st.session_state[key] = value
                    st.success(f"Welcome back, {profile['full_name']}! 🎉")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.error("Please enter both username and password.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_signup:
        st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
        st.subheader("Create your AIR-Bud account")

        signup_name = st.text_input("Full Name", placeholder="John Doe")
        signup_user = st.text_input("Username", placeholder="johndoe")
        signup_email = st.text_input("Email (optional)", placeholder="you@example.com")
        signup_pass = st.text_input("Password", type="password", help="At least 6 characters")
        signup_confirm = st.text_input("Confirm Password", type="password")

        if st.button("Create Account", type="primary", use_container_width=True, key="signup_btn"):
            if not signup_name or not signup_user or not signup_pass:
                st.error("Please fill in all required fields.")
            elif signup_pass != signup_confirm:
                st.error("Passwords do not match.")
            elif len(signup_pass) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                try:
                    profile = create_user(signup_user, signup_name, signup_pass, signup_email)
                    st.session_state["user_logged_in"] = True
                    st.session_state["current_user"] = profile
                    st.success(f"Account created! Welcome, {profile['full_name']}! 🎉")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("🔒 Your data is encrypted and stored locally.")
    st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────
user = st.session_state["current_user"]

with st.sidebar:
    st.markdown(f"### 👋 Hi, {user['full_name']}!")
    st.divider()

    # LLM Configuration
    st.markdown("### ⚙️ AI Settings")

    # Model selection
    available_models = {
        "gpt-4o-mini": "GPT-4o Mini (Fast, recommended)",
        "gpt-4o": "GPT-4o (Best quality)",
        "gpt-4.1-mini": "GPT-4.1 Mini",
        "gpt-3.5-turbo": "GPT-3.5 Turbo (Budget)",
        "custom": "Custom model...",
    }
    selected_model_label = st.selectbox(
        "🤖 Model",
        options=list(available_models.keys()),
        format_func=lambda x: available_models[x],
        help="Choose which AI model to use",
    )

    # API Key
    api_key = st.text_input(
        "🔑 API Key",
        type="password",
        value=st.session_state.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
        help="Your OpenAI API key (sk-...). Stored only in your browser session.",
    )

    # Expandable advanced settings
    with st.expander("🔗 Advanced Settings"):
        base_url = st.text_input(
            "API Base URL",
            value=st.session_state.get("base_url", "https://openai.rc.asu.edu/v1"),
            help="Default: https://openai.rc.asu.edu/v1",
        )
        if selected_model_label == "custom":
            model = st.text_input(
                "Custom Model Name",
                value=st.session_state.get("model", "gpt-4o-mini"),
                help="Enter the exact model name from your API provider",
            )
        else:
            model = selected_model_label
            st.caption(f"Using: `{model}`")

    # Save to session state
    st.session_state["api_key"] = api_key
    st.session_state["base_url"] = base_url
    st.session_state["model"] = model

    st.divider()

    # Quick stats
    st.markdown("### 📊 Your Progress")
    syllabus = st.session_state.get("syllabus_data", {})
    quiz_history = st.session_state.get("quiz_history", [])
    notes = st.session_state.get("uploaded_notes", [])

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Courses", 1 if syllabus else 0)
        st.metric("Quizzes", len(quiz_history))
    with col2:
        st.metric("Notes", len(notes))
        if quiz_history:
            avg = sum(h.get("percentage", 0) for h in quiz_history) / len(quiz_history)
            st.metric("Avg Score", f"{avg:.0f}%")

    st.divider()

    # Settings & Logout
    if st.button("🚪 Sign Out", use_container_width=True):
        # Save state before logging out
        from utils.auth import save_user_state
        state_to_save = {}
        skip_keys = {"user_logged_in", "current_user"}
        for key, value in st.session_state.items():
            if key not in skip_keys:
                try:
                    # Only save JSON-serializable data
                    import json
                    json.dumps(value)
                    state_to_save[key] = value
                except (TypeError, ValueError):
                    pass
        save_user_state(user["username"], state_to_save)

        st.session_state.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("**AIR-Bud** v1.0 🚀")

# ─── Main Content ─────────────────────────────────────────────────────────
col_title, col_mascot = st.columns([3, 1])
with col_title:
    st.markdown('<p class="main-title">🎓 AIR-Bud</p>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Am I Ready? Your AI study companion that turns syllabi into success.</p>', unsafe_allow_html=True)
with col_mascot:
    st.image("assets/mascot-hopeful.png", width=140)

st.divider()

# Feature cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <h3>Upload Syllabus</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">Upload PDF. AI extracts deadlines, exams & topics.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/01_Upload_Syllabus.py", label="Upload Syllabus →", icon="📄")

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📅</div>
        <h3>Timeline & Calendar</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">View timeline. Export to Google Calendar or iCal.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/02_Timeline_Calendar.py", label="View Timeline →", icon="📅")

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <h3>Study Companion</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">AI tutor in Tutor Mode or quick Ask Mode.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/03_Study_Companion.py", label="Chat with AI →", icon="🤖")

with col4:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">❓</div>
        <h3>Mock Quizzes</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">AI-generated quizzes. Track your scores.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/05_Mock_Quiz.py", label="Take Quiz →", icon="❓")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <h3>Notes & Assignments</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">Upload notes for AI-powered study support.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/04_Notes_Assignments.py", label="Upload Notes →", icon="📝")

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <h3>Readiness Check</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">Am I ready for my exam? AI says...</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/06_Readiness_Assessment.py", label="Check Readiness →", icon="📊")

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🗓️</div>
        <h3>Study Plan</h3>
        <p style="color: #6b7280; font-size: 0.9rem;">Personalized day-by-day study schedule.</p>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/07_Study_Plan.py", label="Create Plan →", icon="🗓️")

st.divider()

# Welcome message or status
if not syllabus:
    st.info(
        "💡 **Get started:** Upload a syllabus PDF to unlock everything — timeline, quizzes, "
        "AI tutor, study plans, and readiness assessments."
    )
else:
    course_info = syllabus.get("course_info", {})
    st.success(
        f"✅ **{course_info.get('course_code', '')} {course_info.get('course_name', 'Course')}** loaded! "
        f"Start studying with the tools above."
    )
