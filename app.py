"""
AIR-Bud (Am I Ready) - AI Study/Syllabus Companion
Main Streamlit application entry point.
"""
import streamlit as st
import os
import calendar as cal_mod
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="AIR-Bud | Am I Ready?",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.theme import apply_theme, sidebar_brand, sidebar_nav
from utils.llm_client import chat_completion_stream

apply_theme()

# ─── Onboarding Check ─────────────────────────────────────────────────────
if "user_logged_in" not in st.session_state:
    st.session_state["user_logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None

if not st.session_state["user_logged_in"]:
    from utils.auth import create_user, login_user, load_user_state

    col_logo, col_form = st.columns([1, 2])
    with col_logo:
        st.image("assets/mascot-excited.png", width=200)
    with col_form:
        st.markdown('<p class="page-title">🎓 AIR-Bud</p>', unsafe_allow_html=True)
        st.caption("Am I Ready? Your AI Study Companion.")

        tab_login, tab_signup = st.tabs(["🔑 Sign In", "✨ Create Account"])

        with tab_login:
            st.subheader("Welcome back!")
            login_user_input = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            if st.button("Sign In", type="primary", use_container_width=True, key="login_btn"):
                if login_user_input and login_pass:
                    try:
                        profile = login_user(login_user_input, login_pass)
                        st.session_state["user_logged_in"] = True
                        st.session_state["current_user"] = profile
                        user_state = load_user_state(profile["username"])
                        for key, value in user_state.items():
                            st.session_state[key] = value
                        st.success(f"Welcome back, {profile['full_name']}! 🎉")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                else:
                    st.error("Please enter both username and password.")

        with tab_signup:
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

    st.divider()
    st.caption("🔒 Your data is encrypted and stored locally.")
    st.stop()

# ─── Sidebar ──────────────────────────────────────────────────────────────
user = st.session_state["current_user"]

with st.sidebar:
    sidebar_brand()
    st.markdown("---")
    st.markdown(f"**{user['full_name']}**")
    st.markdown("---")
    sidebar_nav("app.py")
    st.markdown("---")
    st.markdown("### ⚙️ AI Settings")

    api_key = st.text_input(
        "🔑 API Key", type="password",
        value=st.session_state.get("api_key", os.environ.get("OPENAI_API_KEY", "")),
        help="Your API key. Stored only in your browser session.",
    )
    model = st.text_input(
        "🤖 Model Name",
        value=st.session_state.get("model", "gpt-4o-mini"),
        help="Enter the exact model name from your API provider.",
    )
    with st.expander("🔗 Advanced"):
        base_url = st.text_input(
            "API Base URL",
            value=st.session_state.get("base_url", "https://openai.rc.asu.edu/v1"),
            help="Default ASU URL: https://openai.rc.asu.edu/v1",
        )

    st.session_state["api_key"] = api_key
    st.session_state["base_url"] = base_url
    st.session_state["model"] = model

    st.markdown("---")
    if st.button("🚪 Sign Out", use_container_width=True):
        from utils.auth import save_user_state
        state_to_save = {}
        skip_keys = {"user_logged_in", "current_user"}
        for key, value in st.session_state.items():
            if key not in skip_keys:
                try:
                    import json
                    json.dumps(value)
                    state_to_save[key] = value
                except (TypeError, ValueError):
                    pass
        save_user_state(user["username"], state_to_save)
        st.session_state.clear()
        st.rerun()

    st.markdown("**AIR-Bud** v1.0")


# ═══════════════════════════════════════════════════════════════════════════
#  THREE-COLUMN DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════

hour = datetime.now().hour
greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
first_name = user['full_name'].split()[0]

st.markdown(f"<h1 style='color:#8C1515;font-size:1.8rem;margin:0;'>{greeting}, {first_name}!</h1>", unsafe_allow_html=True)
st.caption("Your study overview")
st.divider()

col_calendar, col_actions, col_chat = st.columns([1, 1.2, 1])

# ──────────────────────────────────────────────────────────────────────────
#  LEFT PANE: Calendar + Upcoming Events + Course Info
# ──────────────────────────────────────────────────────────────────────────
with col_calendar:
    now = datetime.now()
    today = now.day
    first_day = datetime(now.year, now.month, 1).weekday()
    days_in_month = cal_mod.monthrange(now.year, now.month)[1]
    month_name = now.strftime("%B %Y")

    syllabus = st.session_state.get("syllabus_data", {})
    key_dates = syllabus.get("key_dates", [])

    event_days = set()
    for event in key_dates:
        try:
            from dateutil.parser import parse as parse_date
            dt = parse_date(event.get("date", ""))
            if dt.month == now.month and dt.year == now.year:
                event_days.add(dt.day)
        except:
            pass

    # Build entire calendar as ONE string
    cal_html = f'<div class="panel"><div class="panel-header">📅 {month_name}</div>'
    cal_html += "<div class='calendar-grid'>"
    for dn in ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]:
        cal_html += f"<div class='calendar-header-cell'>{dn}</div>"
    for _ in range(first_day):
        cal_html += "<div class='calendar-day empty'> </div>"
    for day in range(1, days_in_month + 1):
        cls = "calendar-day"
        if day == today:
            cls += " today"
        elif day in event_days:
            cls += " has-event"
        cal_html += f"<div class='{cls}'>{day}</div>"
    cal_html += "</div>"

    # Events section
    cal_html += "<div class='panel-section'>Upcoming Events</div>"
    if key_dates:
        for event in key_dates[:5]:
            et = event.get("type", "other")
            colors = {"exam": "#ef4444", "midterm": "#ef4444", "final": "#dc2626", "quiz": "#f59e0b", "assignment": "#3b82f6", "project": "#8b5cf6", "deadline": "#f97316", "other": "#6b7280"}
            color = colors.get(et, "#6b7280")
            cal_html += (
                f"<div class='event-item'>"
                f"<div class='event-dot' style='background:{color}'></div>"
                f"<div><strong>{event.get('event_name', 'Event')}</strong><br>"
                f"<span style='color:#6B6B6B;font-size:0.72rem;'>{event.get('date', 'TBD')} • {et}</span></div></div>"
            )
    else:
        cal_html += "<p style='color:#6B6B6B;font-size:0.8rem;'>No events yet. Upload a syllabus.</p>"

    # Course info
    if syllabus:
        ci = syllabus.get("course_info", {})
        cal_html += "<div class='panel-section'>Current Course</div>"
        cal_html += f"<p style='font-weight:700;color:#8C1515;margin:0.25rem 0;'>{ci.get('course_code', '')} {ci.get('course_name', '')}</p>"
        if ci.get("instructor_name"):
            cal_html += f"<p style='color:#6B6B6B;font-size:0.8rem;margin:0;'>Prof. {ci['instructor_name']}</p>"
        topics = syllabus.get("topics", [])
        cal_html += f"<p style='color:#6B6B6B;font-size:0.78rem;margin:0.25rem 0;'>{len(topics)} topics • {len(key_dates)} events</p>"

    cal_html += "</div>"

    st.markdown(cal_html, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
#  CENTER PANE: Stats + Top Actions
# ──────────────────────────────────────────────────────────────────────────
with col_actions:
    quiz_history = st.session_state.get("quiz_history", [])
    notes = st.session_state.get("uploaded_notes", [])
    avg = sum(h.get("percentage", 0) for h in quiz_history) / len(quiz_history) if quiz_history else 0

    center_html = '<div class="panel"><div class="panel-header">⚡ Dashboard</div>'

    # Stats row
    center_html += "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:1rem;'>"
    center_html += f"<div style='text-align:center;padding:12px;background:#F6F6F6;border-radius:8px;'><div class='stat-card-value'>{1 if syllabus else 0}</div><div class='stat-card-label'>Courses</div></div>"
    center_html += f"<div style='text-align:center;padding:12px;background:#F6F6F6;border-radius:8px;'><div class='stat-card-value'>{len(quiz_history)}</div><div class='stat-card-label'>Quizzes</div></div>"
    center_html += f"<div style='text-align:center;padding:12px;background:#F6F6F6;border-radius:8px;'><div class='stat-card-value'>{avg:.0f}{'%' if avg else ''}</div><div class='stat-card-label'>Avg Score</div></div>"
    center_html += "</div>"

    # Quick actions (only top 4, not duplicating all 7)
    center_html += "<div class='panel-section'>Quick Actions</div>"
    actions = [
        ("📄", "Upload Syllabus", "pages/01_Upload_Syllabus.py"),
        ("🤖", "Study Companion", "pages/03_Study_Companion.py"),
        ("❓", "Take a Quiz", "pages/05_Mock_Quiz.py"),
        ("📊", "Readiness Check", "pages/06_Readiness_Assessment.py"),
        ("🗓️", "Study Plan", "pages/07_Study_Plan.py"),
    ]
    for icon, label, path in actions:
        center_html += f'<a href="{path}" class="nav-link" style="display:flex;margin:0;padding:10px 12px;border:1px solid var(--border);border-radius:8px;text-decoration:none;color:var(--text);"><span style="font-size:1.1rem;margin-right:8px;">{icon}</span>{label}</a>'

    center_html += "</div>"
    st.markdown(center_html, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────
#  RIGHT PANE: Persistent AI Assistant
# ──────────────────────────────────────────────────────────────────────────
with col_chat:
    api_key = st.session_state.get("api_key", "")
    base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
    mdl = st.session_state.get("model", "gpt-4o-mini")

    if "chat_messages" not in st.session_state:
        st.session_state["chat_messages"] = [{"role": "assistant", "content": "Hi! I'm AIR-Bud. Ask me anything about your courses. Upload a syllabus to get started!"}]

    chat_html = '<div class="panel"><div class="panel-header ai-chat-header"><span class="ai-status"></span> AIR-Bud Assistant</div>'

    # Chat messages (last 10)
    chat_html += '<div style="max-height:350px;overflow-y:auto;margin-bottom:0.75rem;">'
    for msg in st.session_state.get("chat_messages", [])[-10:]:
        if msg["role"] == "assistant":
            chat_html += f'<div style="padding:8px 12px;margin:4px 0;background:#F6F6F6;border-radius:8px;font-size:0.84rem;"><strong>AIR-Bud:</strong> {msg["content"][:200]}{"..." if len(msg["content"]) > 200 else ""}</div>'
        else:
            chat_html += f'<div style="padding:8px 12px;margin:4px 0;background:rgba(140,21,21,0.06);border-radius:8px;font-size:0.84rem;text-align:right;">{msg["content"][:150]}{"..." if len(msg["content"]) > 150 else ""}</div>'
    chat_html += '</div>'

    st.markdown(chat_html, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Ask AIR-Bud..."):
        st.session_state["chat_messages"].append({"role": "user", "content": prompt})
        context_parts = []
        if syllabus:
            ci = syllabus.get("course_info", {})
            context_parts.append(f"Course: {ci.get('course_code', '')} {ci.get('course_name', '')}")
            topics = syllabus.get("topics", [])
            if topics:
                context_parts.append("Topics:\n" + "\n".join([f"- {t.get('topic_name', '')}" for t in topics]))
            kds = syllabus.get("key_dates", [])
            if kds:
                context_parts.append("Events:\n" + "\n".join([f"- {e.get('event_name', '')}: {e.get('date', '')}" for e in kds]))
        for note in st.session_state.get("uploaded_notes", [])[:3]:
            try:
                fp = note.get("filepath", "")
                if fp and Path(fp).exists():
                    content = Path(fp).read_text(encoding="utf-8", errors="ignore")[:1500]
                    context_parts.append(f"Note ({note.get('filename', '')}):\n{content}")
            except:
                pass
        full_context = "\n\n".join(context_parts) if context_parts else "No course data."

        with st.chat_message("assistant"):
            placeholder = st.empty()
            response = ""
            for chunk in chat_completion_stream(
                user_message=prompt, mode="tutor_mode", context=full_context,
                api_key=api_key, base_url=base_url, model=mdl,
            ):
                response += chunk
                placeholder.markdown(response + "▌")
            placeholder.markdown(response)
        st.session_state["chat_messages"].append({"role": "assistant", "content": response})
        st.rerun()