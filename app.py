import streamlit as st
import pandas as pd
from datetime import date
import json

# --- INITIALIZATION ---
st.set_page_config(page_title="CA Journey Final", layout="wide", page_icon="🎓")

# Ensure all data structures exist
if 'syllabus' not in st.session_state:
    st.session_state.syllabus = {}
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
if 'done' not in st.session_state:
    st.session_state.done = []

# --- 1. DATA BACKUP & RESTORE (The "Save" System) ---
st.sidebar.header("💾 Save & Load")

# Create a dictionary of all your data
current_data = {
    "syllabus": st.session_state.syllabus,
    "logs": st.session_state.logs.to_dict('records'),
    "done": st.session_state.done
}
data_string = json.dumps(current_data)

# Download Button: Saves your progress to a file
st.sidebar.download_button(
    label="📥 Backup to File",
    data=data_string,
    file_name=f"ca_backup_{date.today()}.json",
    mime="application/json"
)

# Upload Button: Restores your progress from that file
uploaded_file = st.sidebar.file_opener = st.sidebar.file_uploader("📂 Restore from File", type="json")
if uploaded_file is not None:
    if st.sidebar.button("Confirm Restore"):
        file_contents = json.load(uploaded_file)
        st.session_state.syllabus = file_contents['syllabus']
        st.session_state.logs = pd.DataFrame(file_contents['logs'])
        st.session_state.done = file_contents['done']
        st.success("Data Restored!")
        st.rerun()

# --- 2. SIDEBAR: ADD SUBJECTS ---
st.sidebar.divider()
with st.sidebar.expander("➕ Add Subject"):
    sub_input = st.text_input("Subject Name")
    topics_input = st.text_area("Topics (comma separated)")
    if st.button("Add Subject"):
        if sub_input and topics_input:
            st.session_state.syllabus[sub_input] = [t.strip() for t in topics_input.split(",") if t.strip()]
            st.rerun()

if st.sidebar.button("🗑️ Reset App"):
    st.session_state.syllabus = {}
    st.session_state.logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
    st.session_state.done = []
    st.rerun()

# --- 3. MAIN INTERFACE ---
st.title("🛡️ My CA Study Tracker")

# SYLLABUS SECTION
st.header("📊 Progress")
if not st.session_state.syllabus:
    st.warning("Add your subjects in the sidebar to begin!")
else:
    # Subjects in columns
    cols = st.columns(len(st.session_state.syllabus))
    for i, (sub, topics) in enumerate(st.session_state.syllabus.items()):
        with cols[i]:
            st.subheader(sub)
            for t in topics:
                # Checkbox logic
                is_finished = t in st.session_state.done
                if st.checkbox(t, value=is_finished, key=f"{sub}_{t}"):
                    if t not in st.session_state.done:
                        st.session_state.done.append(t)
                else:
                    if t in st.session_state.done:
                        st.session_state.done.remove(t)
            
            # Progress Bar
            done_count = len([t for t in topics if t in st.session_state.done])
            total = len(topics)
            if total > 0:
                st.progress(done_count/total)
                st.caption(f"{int((done_count/total)*100)}% Complete")

st.divider()

# LOGGER & HISTORY
col_log, col_hist = st.columns([1, 2])

with col_log:
    st.header("📝 Log Study")
    with st.form("study_form", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        s = st.selectbox("Subject", list(st.session_state.syllabus.keys()) if st.session_state.syllabus else ["None"])
        tp = st.text_input("Topic")
        h = st.number_input("Hours", min_value=0.1, step=0.5)
        if st.form_submit_button("Save"):
            if st.session_state.syllabus:
                new_entry = pd.DataFrame([[d, s, tp, h]], columns=["Date", "Subject", "Topic", "Hours"])
                st.session_state.logs = pd.concat([st.session_state.logs, new_entry], ignore_index=True)
                st.rerun()

with col_hist:
    st.header("📅 Study History")
    if not st.session_state.logs.empty:
        st.dataframe(st.session_state.logs.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
    else:
        st.info("No study history yet.")
