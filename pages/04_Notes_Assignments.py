"""
Page 4: Notes & Assignments Upload
Upload course notes and assignment files for AI-powered study support.
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.auth import save_user_file, get_user_files, save_user_state
from utils.theme import apply_theme

st.set_page_config(page_title="Notes & Assignments - AIR-Bud", page_icon="📝")
apply_theme()

# Auth check
if not st.session_state.get("user_logged_in"):
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Back to Home", icon="🏠")
    st.stop()

user = st.session_state.get("current_user", {})

st.title("📝 Notes & Assignments")
st.caption("AIR-Bud | Am I Ready?")
st.markdown("Upload lecture notes and assignments. The AI companion uses these to answer your questions.")

if not st.session_state.get("syllabus_data", {}):
    st.warning("⚠️ Upload a syllabus first for the best experience.")

st.divider()

# Upload section
uploaded_file = st.file_uploader(
    "Upload a file",
    type=["pdf", "txt", "md", "doc", "docx", "png", "jpg", "jpeg"],
)

file_type = st.selectbox(
    "File type",
    options=["📝 Lecture Notes", "📖 Assignment", "📊 Lecture Slides", "📋 Study Guide", "📁 Other"],
)

if uploaded_file is not None:
    st.info(f"📎 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("✅ Upload File", type="primary", use_container_width=True):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{uploaded_file.name}"
            filepath = save_user_file(user["username"], filename, uploaded_file.getvalue())

            # Add to session state notes list
            if "uploaded_notes" not in st.session_state:
                st.session_state["uploaded_notes"] = []
            st.session_state["uploaded_notes"].append({
                "filepath": filepath,
                "filename": uploaded_file.name,
                "file_type": file_type.split()[-1].lower(),
                "uploaded_at": datetime.now().isoformat(),
            })

            # Auto-save
            save_user_state(user["username"], {
                "uploaded_notes": st.session_state["uploaded_notes"],
                "syllabus_data": st.session_state.get("syllabus_data", {}),
                "quiz_history": st.session_state.get("quiz_history", []),
            })

            st.success(f"✅ Uploaded: `{uploaded_file.name}`")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Upload failed: {e}")

st.divider()

# Display uploaded files
uploaded_files = st.session_state.get("uploaded_notes", [])

if uploaded_files:
    st.subheader(f"📂 Your Files ({len(uploaded_files)})")

    types = list(set(f["file_type"] for f in uploaded_files))
    if len(types) > 1:
        filter_type = st.selectbox("Filter by type", ["All"] + types)
        if filter_type != "All":
            display_files = [f for f in uploaded_files if f["file_type"] == filter_type]
        else:
            display_files = uploaded_files
    else:
        display_files = uploaded_files

    for i, file_info in enumerate(display_files):
        filepath = file_info.get("filepath", "")
        filename = file_info.get("filename", "unknown")
        ftype = file_info.get("file_type", "note")
        uploaded_at = file_info.get("uploaded_at", "unknown")[:10]

        file_emoji = {"lecture notes": "📝", "assignment": "📖", "lecture slides": "📊",
                       "study guide": "📋", "other": "📁"}.get(ftype.lower(), "📄")

        with st.expander(f"{file_emoji} {filename}  •  {ftype}  •  {uploaded_at}"):
            if filepath and Path(filepath).exists():
                try:
                    if filepath.endswith(".pdf"):
                        st.info("📄 PDF — used by AI companion.")
                    elif filepath.endswith((".txt", ".md")):
                        content = Path(filepath).read_text(encoding="utf-8", errors="ignore")
                        st.code(content[:2000] + ("\n... [truncated]" if len(content) > 2000 else ""), language=None)
                    elif filepath.endswith((".png", ".jpg", ".jpeg")):
                        st.image(filepath, caption=filename, use_container_width=True)
                    else:
                        st.info(f"📄 {ftype} — used by AI companion.")
                except Exception:
                    st.info("📄 File uploaded.")
            else:
                st.warning("⚠️ File not found on disk.")

            if st.button(f"🗑️ Delete", key=f"del_{i}"):
                uploaded_files.pop(i)
                st.session_state["uploaded_notes"] = uploaded_files
                save_user_state(user["username"], {"uploaded_notes": uploaded_files})
                st.rerun()
else:
    st.info("📭 No files uploaded yet.")

st.divider()

# Summary
if uploaded_files:
    st.subheader("📊 Summary")
    type_counts = {}
    for f in uploaded_files:
        ft = f.get("file_type", "other")
        type_counts[ft] = type_counts.get(ft, 0) + 1
    cols = st.columns(min(len(type_counts), 4))
    for i, (ft, count) in enumerate(type_counts.items()):
        cols[i % len(cols)].metric(f"{ft.title()}", count)
