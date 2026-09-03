"""
Page 2: Timeline & Calendar Export
View extracted timeline and export to Google Calendar or iCal.
"""
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.calendar_exporter import generate_ics, generate_google_calendar_url
from utils.theme import apply_theme

st.set_page_config(page_title="Timeline & Calendar - AIR-Bud", page_icon="📅")
apply_theme()

# Auth check
if not st.session_state.get("user_logged_in"):
    st.warning("⚠️ Please sign in first.")
    st.page_link("app.py", label="← Back to Home", icon="🏠")
    st.stop()

st.title("📅 Timeline & Calendar Export")
st.caption("AIR-Bud | Am I Ready?")

# Check for syllabus data
syllabus_data = st.session_state.get("syllabus_data", {})
if not syllabus_data:
    st.warning("⚠️ No syllabus data found. Please upload a syllabus first.")
    st.page_link("pages/01_Upload_Syllabus.py", label="Upload Syllabus", icon="📄")
    st.stop()

course_info = syllabus_data.get("course_info", {})
key_dates = syllabus_data.get("key_dates", [])

if not key_dates:
    st.info("ℹ️ No key dates were extracted from the syllabus.")
    st.stop()

type_emojis = {
    "exam": "📝", "midterm": "📝", "final": "🏁",
    "quiz": "❓", "assignment": "📖", "project": "🚀",
    "presentation": "🎤", "deadline": "⏰", "other": "📌"
}
type_colors = {
    "exam": "#ef4444", "midterm": "#ef4444", "final": "#dc2626",
    "quiz": "#f59e0b", "assignment": "#3b82f6", "project": "#8b5cf6",
    "presentation": "#ec4899", "deadline": "#f97316", "other": "#6b7280"
}

# Timeline view
st.subheader("📋 Course Timeline")

for event in key_dates:
    emoji = type_emojis.get(event.get("type", "other"), "📌")
    weight = event.get("weight")

    cols = st.columns([1, 3, 1, 2])
    cols[0].write(f"{emoji}")
    cols[1].write(f"**{event.get('event_name', 'Event')}**")
    cols[2].write(f"`{event.get('type', 'other')}`")
    cols[3].write(f"📅 {event.get('date', 'TBD')}")

    if event.get("description"):
        st.caption(f"   {event['description']}")
    st.divider()

# Statistics
st.subheader("📊 Timeline Summary")
type_counts = {}
for event in key_dates:
    t = event.get("type", "other")
    type_counts[t] = type_counts.get(t, 0) + 1

stat_cols = st.columns(min(len(type_counts), 4))
for i, (t, count) in enumerate(type_counts.items()):
    emoji = type_emojis.get(t, "📌")
    stat_cols[i % len(stat_cols)].metric(f"{emoji} {t.upper()}", count)

st.divider()

# Calendar Export
st.subheader("📤 Export to Calendar")

event_duration = st.slider("Default event duration (hours)", 1, 8, 2)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📅 Download iCal (.ics)")
    st.caption("Import into Apple Calendar, Outlook, or any calendar app.")
    if st.button("⬇️ Download .ics File", type="primary", use_container_width=True):
        try:
            ics_bytes = generate_ics(syllabus_data, event_duration)
            st.download_button(
                label="✅ Save .ics File",
                data=ics_bytes,
                file_name=f"{course_info.get('course_code', 'course')}_schedule.ics",
                mime="text/calendar",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error generating .ics: {e}")

with col2:
    st.markdown("### 🔗 Google Calendar")
    st.caption("Add each event directly to Google Calendar.")
    try:
        gc_urls = generate_google_calendar_url(syllabus_data, event_duration)
        if gc_urls:
            for evt in gc_urls:
                emoji = type_emojis.get(evt.get("event_type", "other"), "📌")
                st.markdown(
                    f"[{emoji} Add: {evt['event_name']} ({evt.get('date', 'TBD')})](%s)" % evt["url"]
                )
        else:
            st.info("No events with valid dates found.")
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()

# Table view toggle
if st.toggle("Show as table", value=False):
    import pandas as pd
    df_data = []
    for event in key_dates:
        df_data.append({
            "Event": event.get("event_name", "Event"),
            "Type": event.get("type", "other"),
            "Date": event.get("date", "TBD"),
            "Weight": f"{event.get('weight', 'N/A')}%" if event.get("weight") else "N/A",
        })
    st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
