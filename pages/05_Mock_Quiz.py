"""
Page 5: Mock Quiz Generator
Generate and take AI-powered mock quizzes based on your syllabus.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.llm_client import structured_output
from utils.auth import save_user_state
from utils.theme import apply_theme, sidebar_brand, sidebar_nav

st.set_page_config(page_title="Mock Quiz - AIR-Bud", page_icon="❓")
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
    sidebar_nav("pages/05_Mock_Quiz.py")

st.title("❓ Mock Quiz Generator")
st.caption("AIR-Bud | Am I Ready?")

# API config
api_key = st.session_state.get("api_key", "")
base_url = st.session_state.get("base_url", "https://openai.rc.asu.edu/v1")
model = st.session_state.get("model", "gpt-4o-mini")

if not api_key:
    st.warning("⚠️ Please enter your API key in the sidebar first.")
    st.stop()

syllabus = st.session_state.get("syllabus_data", {})
if not syllabus:
    st.warning("⚠️ No syllabus found. Upload a syllabus for targeted quizzes.")

st.divider()

# Quiz config
col1, col2, col3 = st.columns(3)
with col1:
    num_questions = st.number_input("Number of questions", min_value=1, max_value=30, value=5)
with col2:
    difficulty = st.selectbox("Difficulty", ["easy", "medium", "hard", "mixed"])
with col3:
    quiz_topic = st.selectbox(
        "Topic focus",
        ["All Topics"] + [t.get("topic_name", "Unknown") for t in syllabus.get("topics", [])],
    )

# Generate quiz
if st.button("🎲 Generate Quiz", type="primary", use_container_width=True):
    topics_text = "\n".join([f"- {t.get('topic_name', '')}: {t.get('description', '')}"
                             for t in syllabus.get("topics", [])]) if syllabus.get("topics") else ""

    topic_filter = f"\n\nFocus ONLY on: {quiz_topic}" if quiz_topic != "All Topics" else ""

    prompt = (f"Generate {num_questions} mock quiz questions.\nDifficulty: {difficulty}\n{topic_filter}\n\n"
              f"Course topics:\n{topics_text}")

    with st.spinner("🤖 Generating quiz..."):
        try:
            questions = structured_output(
                user_message=prompt, prompt_name="quiz_generator",
                api_key=api_key, base_url=base_url, model=model,
            )
            if isinstance(questions, list):
                st.session_state["current_quiz"] = questions
            elif isinstance(questions, dict):
                quiz_list = questions.get("questions", questions.get("quiz", list(questions.values())))
                st.session_state["current_quiz"] = quiz_list if isinstance(quiz_list, list) else list(questions.values())
            else:
                st.session_state["current_quiz"] = []

            st.session_state["quiz_answered"] = [False] * len(st.session_state["current_quiz"])
            st.session_state["quiz_user_answers"] = [None] * len(st.session_state["current_quiz"])

            st.success(f"✅ Generated {len(st.session_state['current_quiz'])} questions!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed: {e}")

# Display quiz
if "current_quiz" in st.session_state and st.session_state["current_quiz"]:
    st.divider()
    quiz = st.session_state["current_quiz"]
    st.subheader(f"📝 Quiz ({len(quiz)} questions)")

    total_score = 0
    total_points = 0

    for i, q in enumerate(quiz):
        question_text = q.get("question_text", q.get("question", f"Question {i+1}"))
        q_type = q.get("question_type", q.get("type", "multiple_choice"))
        topic = q.get("topic", "General")
        points = q.get("points", 5)
        total_points += points

        st.markdown(f"**Q{i+1}.** [{topic}] ({points} pts)")
        st.write(question_text)

        answered = st.session_state.get("quiz_answered", [False] * len(quiz))[i]
        user_answer = st.session_state.get("quiz_user_answers", [None] * len(quiz))[i]

        if q_type == "multiple_choice" and "options" in q:
            options = q["options"]
            if isinstance(options, dict):
                opt_vals = list(options.values())
            else:
                opt_vals = options[:4]

            if not answered:
                user_answer = st.radio("Your answer:", options=opt_vals, index=None, key=f"quiz_{i}_ans")
                if user_answer and st.button("Submit", key=f"quiz_{i}_sub"):
                    st.session_state["quiz_answered"][i] = True
                    st.session_state["quiz_user_answers"][i] = user_answer
                    st.rerun()

            if answered:
                correct = q.get("correct_answer", q.get("answer", ""))
                is_correct = str(user_answer).strip() == str(correct).strip()
                if is_correct:
                    total_score += points
                    st.success(f"✅ Correct! ({user_answer})")
                else:
                    st.error(f"❌ Incorrect. You said: {user_answer} | Answer: {correct}")
                if q.get("explanation"):
                    st.info(f"💡 {q['explanation']}")

        elif q_type == "true_false":
            if not answered:
                user_answer = st.radio("Your answer:", ["True", "False"], index=None, key=f"quiz_{i}_ans")
                if user_answer and st.button("Submit", key=f"quiz_{i}_sub"):
                    st.session_state["quiz_answered"][i] = True
                    st.session_state["quiz_user_answers"][i] = user_answer
                    st.rerun()
            if answered:
                correct = str(q.get("correct_answer", "")).lower()
                is_correct = user_answer.lower() == correct
                if is_correct:
                    total_score += points
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Answer: {q.get('correct_answer', '')}")
                if q.get("explanation"):
                    st.info(f"💡 {q['explanation']}")

        else:
            if not answered:
                user_answer = st.text_area("Your answer:", key=f"quiz_{i}_ans")
                if user_answer and st.button("Submit & Check", key=f"quiz_{i}_sub"):
                    st.session_state["quiz_answered"][i] = True
                    st.session_state["quiz_user_answers"][i] = user_answer
                    st.rerun()
            if answered:
                st.info(f"💡 Model answer: {q.get('correct_answer', q.get('answer', ''))}")
                if q.get("explanation"):
                    st.info(f"📖 {q['explanation']}")

    # Score
    all_answered = all(st.session_state.get("quiz_answered", []))
    if all_answered and len(quiz) > 0:
        st.divider()
        pct = (total_score / total_points * 100) if total_points > 0 else 0
        emoji = "🎉" if pct >= 80 else "👍" if pct >= 60 else "📚" if pct >= 40 else "💪"
        st.success(f"{emoji} **Score: {total_score}/{total_points} ({pct:.0f}%)**")

        # Save result
        if "quiz_history" not in st.session_state:
            st.session_state["quiz_history"] = []
        st.session_state["quiz_history"].append({
            "topic": quiz_topic, "score": total_score, "total": total_points,
            "percentage": pct, "date": st.session_state.get("_quiz_date", "now"),
            "num_questions": len(quiz),
        })

        if st.button("🔄 New Quiz", use_container_width=True):
            for k in ["current_quiz", "quiz_answered", "quiz_user_answers"]:
                st.session_state.pop(k, None)
            st.rerun()

# Quiz history
st.divider()
st.subheader("📊 Quiz History")
history = st.session_state.get("quiz_history", [])
if history:
    import pandas as pd
    df = pd.DataFrame([{
        "Topic": h.get("topic", "General"), "Score": f"{h.get('score', 0)}/{h.get('total', 0)}",
        "Pct": f"{h.get('percentage', 0):.0f}%", "Qs": h.get("num_questions", 0),
    } for h in history])
    st.dataframe(df, use_container_width=True, hide_index=True)
    avg = sum(h.get("percentage", 0) for h in history) / len(history)
    st.metric("Average Score", f"{avg:.1f}%")
else:
    st.info("📭 No quizzes yet!")
