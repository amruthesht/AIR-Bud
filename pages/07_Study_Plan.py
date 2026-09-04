"""
Page 7: Study Plan Generator
Create AI-powered personalized study plans.
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llm_client import structured_output
from utils.auth import save_user_state
from utils.theme import apply_theme, sidebar_brand, sidebar_nav

st.set_page_config(page_title="Study Plan - AIR-Bud", page_icon="🗓️")
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
    sidebar_nav("pages/07_Study_Plan.py")

st.title("🗓️ AI Study Plan Generator")
st.caption("AIR-Bud | Am I Ready?")

api_key = st.session_state.get("api_key", "")
base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
model = st.session_state.get("model", "gpt-4o-mini")

if not api_key:
    st.warning("⚠️ Enter your API key in the sidebar first.")
    st.stop()

syllabus = st.session_state.get("syllabus_data", {})
if not syllabus:
    st.warning("⚠️ Upload a syllabus for a personalized plan.")

st.divider()

st.subheader("Your Study Preferences")

col1, col2, col3 = st.columns(3)
with col1:
    hours_per_day = st.number_input("Hours/day available", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
with col2:
    start_date = st.date_input("Start date", value=datetime.now().date())
with col3:
    days_to_plan = st.number_input("Days to plan", min_value=1, max_value=90, value=14)

key_dates = syllabus.get("key_dates", [])
exam_events = [e for e in key_dates if e.get("type") in ["exam", "midterm", "final", "quiz"]]

if exam_events:
    target_event = st.selectbox(
        "Plan toward:",
        ["General Plan"] + [f"{e.get('event_name', '')} ({e.get('date', '')})" for e in exam_events],
    )
else:
    target_event = "General Plan"

learning_style = st.selectbox("Learning style", [
    "📖 Reading-heavy", "🎥 Visual", "🗣️ Discussion-based",
    "✍️ Practice-based", "🔄 Mixed",
])

quiz_history = st.session_state.get("quiz_history", [])

weak_areas = st.text_area("Topics you struggle with? (optional)")
strong_areas = st.text_area("Topics you're good at? (optional)")

if st.button("🗓️ Generate Study Plan", type="primary", use_container_width=True):
    topics_text = "\n".join([f"- {t.get('topic_name', '')}: {t.get('description', '')}"
                             for t in syllabus.get("topics", [])]) if syllabus.get("topics") else ""
    dates_text = "\n".join([f"- {e.get('event_name', '')}: {e.get('date', '')}"
                            for e in key_dates]) if key_dates else "None"
    quiz_text = "\n".join([f"- {h.get('topic', '')}: {h.get('percentage', 0):.0f}%"
                           for h in quiz_history]) if quiz_history else "No data"

    prompt = (f"Create a study plan:\n\nTopics:\n{topics_text}\n\nKey dates:\n{dates_text}\n\n"
              f"Quiz scores:\n{quiz_text}\n\nPreferences:\n"
              f"- Hours/day: {hours_per_day}\n- Start: {start_date}\n- Duration: {days_to_plan} days\n"
              f"- Target: {target_event}\n- Style: {learning_style}\n"
              f"- Weak: {weak_areas or 'None'}\n- Strong: {strong_areas or 'None'}\n\n"
              f"Generate a detailed day-by-day plan.")

    with st.spinner("🤖 Generating plan..."):
        try:
            plan = structured_output(user_message=prompt, prompt_name="study_plan",
                                      api_key=api_key, base_url=base_url, model=model)
            st.session_state["study_plan"] = plan
            st.success("✅ Plan generated!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {e}")

# Display plan
plan = st.session_state.get("study_plan", {})
if plan:
    st.divider()
    st.subheader("📋 Your Study Plan")

    overview = plan.get("plan_overview", "")
    if overview:
        st.info(overview)

    total_hours = plan.get("total_study_hours", 0)
    if total_hours:
        st.metric("Total Hours", f"{total_hours}h")

    sessions = plan.get("sessions", [])
    if sessions:
        st.subheader("📅 Schedule")
        by_date = {}
        for s in sessions:
            if isinstance(s, dict):
                dk = s.get("date", s.get("day", "?"))
                topic = s.get("topic", s.get("focus", "Review"))
                dur = s.get("duration", s.get("hours", "?"))
                desc = s.get("description", s.get("details", ""))
                pri = s.get("priority", "medium")
            else:
                dk = s[0] if len(s) > 0 else "?"
                topic = s[1] if len(s) > 1 else "Review"
                dur = s[2] if len(s) > 2 else "?"
                pri = s[3] if len(s) > 3 else "medium"
                desc = s[4] if len(s) > 4 else ""
            by_date.setdefault(dk, []).append({"topic": topic, "duration": dur,
                                                 "description": desc, "priority": pri})

        for dk, day_sess in by_date.items():
            with st.expander(f"📅 {dk} ({len(day_sess)} sessions)"):
                for s in day_sess:
                    p_e = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(s["priority"].lower(), "⚪")
                    st.markdown(f"- {p_e} **{s['topic']}** ({s['duration']})")
                    if s["description"]:
                        st.caption(f"   {s['description']}")

    milestones = plan.get("milestones", [])
    if milestones:
        st.subheader("🏁 Milestones")
        for m in milestones:
            txt = m if isinstance(m, str) else m.get("milestone", m.get("name", "Milestone"))
            st.write(f"- 🏁 {txt}")

    tips = plan.get("tips", [])
    if tips:
        st.subheader("💡 Tips")
        for t in tips:
            txt = t if isinstance(t, str) else t.get("tip", t.get("advice", str(t)))
            st.write(f"- 💡 {txt}")

    st.divider()
    if st.button("🔄 Regenerate", use_container_width=True):
        del st.session_state["study_plan"]
        st.rerun()
