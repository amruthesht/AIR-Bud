"""
Page 3: AI Study Companion
Chat with the AI in Tutor Mode or Ask Mode, grounded in your syllabus.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llm_client import chat_completion_stream
from utils.auth import save_user_state
from utils.theme import apply_theme, sidebar_brand, sidebar_nav

st.set_page_config(page_title="Study Companion - AIR-Bud", page_icon="🤖")
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
    sidebar_nav("pages/03_Study_Companion.py")

st.title("🤖 AI Study Companion")
st.caption("AIR-Bud | Am I Ready?")

# API config
api_key = st.session_state.get("api_key", "")
base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
model = st.session_state.get("model", "gpt-4o-mini")

if not api_key:
    st.warning("⚠️ Please enter your API key in the sidebar (⚙️ AI Settings) first.")
    st.stop()

# Mode selection (define BEFORE using in mascot display)
mode = st.radio(
    "Chat Mode",
    options=["🧑‍🏫 Tutor Mode", "⚡ Ask Mode"],
    horizontal=True,
    help="Tutor Mode: Guides you to understand. Ask Mode: Direct, concise answers.",
)
mode_key = "tutor_mode" if "Tutor" in mode else "ask_mode"

# Show mascot based on mode
col_mascot, col_info = st.columns([1, 3])
with col_mascot:
    if "Tutor" in mode:
        st.image("assets/mascot-hopeful.png", width=120, caption="🧑‍🏫 Tutor Mode")
    else:
        st.image("assets/mascot-excited.png", width=120, caption="⚡ Ask Mode")

with col_info:
    # Build context from syllabus + notes
    context_parts = []
    syllabus = st.session_state.get("syllabus_data", {})

    if syllabus:
        course_info = syllabus.get("course_info", {})
        context_parts.append(f"Course: {course_info.get('course_code', '')} {course_info.get('course_name', '')}")
        context_parts.append(f"Instructor: {course_info.get('instructor_name', 'N/A')}")
        context_parts.append(f"Semester: {course_info.get('semester', 'N/A')}")

        topics = syllabus.get("topics", [])
        if topics:
            topic_text = "\n".join([f"- {t.get('topic_name', '')}: {t.get('description', '')}" for t in topics])
            context_parts.append(f"Topics:\n{topic_text}")

        key_dates = syllabus.get("key_dates", [])
        if key_dates:
            dates_text = "\n".join([f"- {e.get('event_name', '')} ({e.get('type', '')}): {e.get('date', '')}" for e in key_dates])
            context_parts.append(f"Key Dates:\n{dates_text}")

        policies = syllabus.get("policies", [])
        if policies:
            context_parts.append(f"Policies:\n" + "\n".join([f"- {p}" for p in policies]))

    # Notes context
    notes = st.session_state.get("uploaded_notes", [])
    for note in notes:
        try:
            filepath = note.get("filepath", "")
            if filepath and Path(filepath).exists():
                content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
                if len(content) > 2000:
                    content = content[:2000] + "\n... [truncated]"
                context_parts.append(f"Student Note ({note.get('filename', 'note')}):\n{content}")
        except Exception:
            pass

    full_context = "\n\n".join(context_parts) if context_parts else "No course context available."

    # Context status
    if context_parts:
        st.success(f"📚 Grounded in: {len(syllabus.get('topics', []))} topics, {len(syllabus.get('key_dates', []))} events, {len(notes)} notes")
    else:
        st.info("ℹ️ Upload a syllabus for a better experience.")

st.divider()

# Initialize chat history
if "companion_messages" not in st.session_state:
    st.session_state["companion_messages"] = []

# Display chat history
for msg in st.session_state.get("companion_messages", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about your course..."):
    st.session_state["companion_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in chat_completion_stream(
            user_message=prompt,
            mode=mode_key,
            context=full_context,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7,
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state["companion_messages"].append({"role": "assistant", "content": full_response})

# Clear chat
if st.button("🗑️ Clear Chat", use_container_width=True):
    st.session_state["companion_messages"] = []
    st.rerun()

# Sidebar info
with st.sidebar:
    st.markdown("### 💡 Tips")
    if "Tutor" in mode:
        st.info("🧑‍🏫 **Tutor Mode** explains concepts step-by-step. Ask 'why' questions!")
    else:
        st.info("⚡ **Ask Mode** gives direct answers. Good for quick facts.")
    st.divider()
    st.markdown("**Context loaded:**")
    syllabus = st.session_state.get("syllabus_data", {})
    notes = st.session_state.get("uploaded_notes", [])
    if syllabus:
        st.write(f"✅ Syllabus ({syllabus.get('course_code', '')})")
    else:
        st.write("❌ No syllabus")
    if notes:
        st.write(f"✅ {len(notes)} note(s)")
    else:
        st.write("❌ No notes")
