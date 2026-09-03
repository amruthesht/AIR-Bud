"""
Page 6: Readiness Assessment
Assess how prepared the student is for upcoming exams/quizzes.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llm_client import structured_output
from utils.auth import save_user_state
from utils.theme import apply_theme

st.set_page_config(page_title="Readiness Assessment - AIR-Bud", page_icon="📊")
apply_theme()

# Auth check
if not st.session_state.get("user_logged_in"):
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Back to Home", icon="🏠")
    st.stop()

user = st.session_state.get("current_user", {})

st.title("📊 Exam Readiness Assessment")
st.caption("AIR-Bud | Am I Ready?")

api_key = st.session_state.get("api_key", "")
base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
model = st.session_state.get("model", "gpt-4o-mini")

if not api_key:
    st.warning("⚠️ Enter your API key in the sidebar first.")
    st.stop()

syllabus = st.session_state.get("syllabus_data", {})
if not syllabus:
    st.warning("⚠️ Upload a syllabus for a full assessment.")

st.divider()

# Config
st.subheader("Configure Assessment")
key_dates = syllabus.get("key_dates", [])
exam_events = [e for e in key_dates if e.get("type") in ["exam", "midterm", "final", "quiz"]]

if exam_events:
    target_event = st.selectbox(
        "Assess readiness for:",
        [f"{e.get('event_name', 'Event')} ({e.get('date', 'TBD')})" for e in exam_events],
    )
else:
    target_event = "Overall Course Readiness"

col1, col2 = st.columns(2)
with col1:
    hours_studied = st.number_input("Hours studied this week", min_value=0.0, value=0.0, step=0.5)
with col2:
    confidence = st.slider("How confident do you feel?", 0, 100, 50)

self_notes = st.text_area("Areas you're struggling with? (optional)",
                           placeholder="e.g., I don't understand recursion...")

quiz_history = st.session_state.get("quiz_history", [])
notes = st.session_state.get("uploaded_notes", [])

st.divider()

if st.button("🔍 Run Readiness Assessment", type="primary", use_container_width=True):
    topics_text = "\n".join([f"- {t.get('topic_name', '')}: {t.get('description', '')}"
                             for t in syllabus.get("topics", [])]) if syllabus.get("topics") else ""
    quiz_text = "\n".join([f"- {h.get('topic', '')}: {h.get('percentage', 0):.0f}%"
                           for h in quiz_history]) if quiz_history else "No quiz data"

    prompt = (f"Assess readiness for: {target_event}\n\n"
              f"Topics:\n{topics_text}\n\nQuiz scores:\n{quiz_text}\n\n"
              f"Notes/assignments: {len(notes)} files\n\n"
              f"Hours studied: {hours_studied}\nConfidence: {confidence}%\n"
              f"Concerns: {self_notes if self_notes else 'None'}\n\nProvide detailed assessment.")

    with st.spinner("🤖 Analyzing readiness..."):
        try:
            assessment = structured_output(user_message=prompt, prompt_name="readiness_assessment",
                                           api_key=api_key, base_url=base_url, model=model)
            st.session_state["readiness_assessment"] = assessment
            st.success("✅ Done!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {e}")

# Display
assessment = st.session_state.get("readiness_assessment", {})
if assessment:
    st.subheader("📋 Readiness Report")
    score = assessment.get("overall_readiness_score", 0)
    level = assessment.get("readiness_level", "unknown").replace("_", " ").title()
    conf = assessment.get("confidence_level", "medium").title()

    emojis = {"Not Prepared": "🔴", "Barely Prepared": "🟠", "Moderately Prepared": "🟡",
              "Well Prepared": "🟢", "Fully Prepared": "🟢"}
    emoji = emojis.get(level, "⚪")

    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score}/100")
    col2.metric("Level", f"{emoji} {level}")
    col3.metric("Confidence", conf)
    st.progress(score / 100)

    topic_bd = assessment.get("topic_breakdown", [])
    if topic_bd:
        st.subheader("📚 Topic Mastery")
        for t in topic_bd:
            tname = t.get("topic_name", t.get("name", "?"))
            mastery = t.get("mastery_percentage", t.get("mastery", 0))
            strength = t.get("strength_level", "?").title()
            s_emoji = {"Strong": "💪", "Moderate": "👌", "Weak": "⚠️"}.get(strength, "❓")
            st.write(f"**{tname}:** {s_emoji} {strength} ({mastery}%)")
            st.progress(mastery / 100)

    weak = assessment.get("weak_areas", [])
    if weak:
        st.subheader("⚠️ Needs Attention")
        for a in weak:
            txt = a if isinstance(a, str) else a.get("topic", a.get("reason", "N/A"))
            st.warning(f"- {txt}")

    strong = assessment.get("strong_areas", [])
    if strong:
        st.subheader("💪 Strengths")
        for a in strong:
            txt = a if isinstance(a, str) else a.get("topic", a.get("name", "N/A"))
            st.success(f"✅ {txt}")

    recs = assessment.get("recommendations", [])
    if recs:
        st.subheader("🎯 Next Steps")
        for i, r in enumerate(recs, 1):
            txt = r if isinstance(r, str) else r.get("action", r.get("tip", str(r)))
            st.write(f"{i}. {txt}")

    st.divider()
    if st.button("🔄 Re-run", use_container_width=True):
        del st.session_state["readiness_assessment"]
        st.rerun()
