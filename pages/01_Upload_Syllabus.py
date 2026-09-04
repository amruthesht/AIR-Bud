"""
Page 1: Upload Syllabus
Upload a course syllabus PDF and extract structured timeline data.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.syllabus_parser import parse_syllabus
from utils.auth import save_user_state, load_user_state
from utils.theme import apply_theme, sidebar_brand, sidebar_nav

st.set_page_config(page_title="Upload Syllabus - AIR-Bud", page_icon="📄")
apply_theme()

# Auth check
if not st.session_state.get("user_logged_in"):
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Back to Home", icon="🏠")
    st.stop()

user = st.session_state.get("current_user", {})

# Sidebar
with st.sidebar:
    sidebar_brand()
    sidebar_nav("pages/01_Upload_Syllabus.py")

st.title("📄 Upload Your Syllabus")
st.caption("AIR-Bud | Am I Ready?")

# API config from session state
api_key = st.session_state.get("api_key", "")
base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
model = st.session_state.get("model", "gpt-4o-mini")

if not api_key:
    st.warning("⚠️ Please enter your API key in the sidebar (⚙️ AI Settings) first.")

# Show existing syllabus if already parsed
syllabus_data = st.session_state.get("syllabus_data", {})
if syllabus_data:
    course_info = syllabus_data.get("course_info", {})
    st.success(
        f"✅ **{course_info.get('course_code', '')} {course_info.get('course_name', 'Course')}** "
        f"is loaded. Upload another to replace it."
    )

st.divider()

# File uploader
uploaded_file = st.file_uploader(
    "Choose a syllabus PDF",
    type=["pdf"],
    help="Upload a course syllabus in PDF format",
)

if uploaded_file is not None and api_key:
    st.info(f"📎 File: `{uploaded_file.name}` ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("🔍 Parse Syllabus with AI", type="primary", use_container_width=True):
        try:
            with st.spinner("🤖 Analyzing syllabus... This takes ~15 seconds"):
                pdf_bytes = uploaded_file.read()
                result = parse_syllabus(pdf_bytes, api_key=api_key, base_url=base_url, model=model)
                st.session_state["syllabus_data"] = result
                # Auto-save
                save_user_state(user["username"], dict(st.session_state))

            st.success("✅ Syllabus parsed successfully!")
            st.rerun()

        except ValueError as e:
            st.error(f"⚠️ {e}")
        except Exception as e:
            st.error(f"❌ Error parsing syllabus: {e}")

elif uploaded_file is not None:
    st.warning("🔑 Enter your API key in the sidebar first, then click Parse.")

# Display parsed data
if syllabus_data:
    st.divider()
    st.subheader("📋 Parsed Syllabus Data")

    # Course Info
    course_info = syllabus_data.get("course_info", {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Course", f"{course_info.get('course_code', 'N/A')}")
    with col2:
        st.metric("Instructor", f"{course_info.get('instructor_name', 'N/A')}")
    with col3:
        st.metric("Semester", f"{course_info.get('semester', 'N/A')}")

    if course_info.get("description"):
        st.write(f"**Description:** {course_info['description']}")

    # Key Dates
    key_dates = syllabus_data.get("key_dates", [])
    if key_dates:
        st.subheader(f"📅 Key Dates ({len(key_dates)} events)")
        type_emojis = {
            "exam": "📝", "midterm": "📝", "final": "🏁",
            "quiz": "❓", "assignment": "📝", "project": "🚀",
            "presentation": "🎤", "deadline": "⏰", "other": "📌"
        }
        for event in key_dates:
            emoji = type_emojis.get(event.get("type", "other"), "📌")
            weight = f" ({event['weight']}%)" if event.get("weight") else ""
            st.markdown(
                f"- {emoji} **{event.get('event_name', 'Event')}{weight}** "
                f"— {event.get('date', 'TBD')} `{event.get('type', 'other')}`"
            )
            if event.get("description"):
                st.caption(f"   {event['description']}")

    # Topics
    topics = syllabus_data.get("topics", [])
    if topics:
        st.subheader(f"📚 Course Topics ({len(topics)} topics)")
        for i, topic in enumerate(topics, 1):
            week = f" (Week {topic['week']})" if topic.get("week") else ""
            st.markdown(f"**{i}. {topic.get('topic_name', 'Topic')}{week}**")
            if topic.get("description"):
                st.caption(f"   {topic['description']}")

    # Policies
    policies = syllabus_data.get("policies", [])
    if policies:
        st.subheader("📜 Policies")
        for policy in policies:
            st.write(f"- {policy}")

    # Clear button
    st.divider()
    if st.button("🗑️ Clear Syllabus", use_container_width=True):
        st.session_state["syllabus_data"] = {}
        save_user_state(user["username"], dict(st.session_state))
        st.rerun()
