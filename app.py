
import streamlit as st
import pandas as pd
from datetime import date
import time
import plotly.express as px
import json

# --- 1. INITIALIZATION ---
st.set_page_config(page_title="CA Journey Pro", layout="wide", page_icon="🎓")

if 'syllabus' not in st.session_state:
    st.session_state.syllabus = {}
if 'logs' not in st.session_state:
    st.session_state.logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
if 'done' not in st.session_state:
    st.session_state.done = []

# --- 2. DATA PERSISTENCE (THE SAVE/LOAD FEATURE) ---
st.sidebar.header("💾 Data Management")

# Generating a "Save String" so the user can copy-paste their progress
data_to_save = {
    "syllabus": st.session_state.syllabus,
    "logs": st.session_state.logs.to_json(),
    "done": st.session_state.done
}
save_string = json.dumps(data_to_save)

with st.sidebar.expander("📥 Save / Restore Progress"):
    st.write("Copy this code to your notes to backup your data:")
    st.code(save_string, language="text")
    
    load_input = st.text_area("Paste your backup code here to restore:")
    if st.button("Restore Session"):
        try:
            loaded_data = json.loads(load_input)
            st.session_state.syllabus = loaded_data['syllabus']
            st.session_state.logs = pd.read_json(loaded_data['logs'])
            st.session_state.done = loaded_data['done']
            st.success("Data Restored!")
            st.rerun()
        except:
            st.error("Invalid code!")

# --- 3. SIDEBAR: SETUP ---
st.sidebar.divider()
with st.sidebar.expander("➕ Add Subject & Syllabus"):
    sub_name = st.text_input("Subject Name")
    sub_topics = st.text_area("Topics (comma separated)")
    if st.button("Add to App"):
        if sub_name and sub_topics:
            st.session_state.syllabus[sub_name] = [t.strip() for t in sub_topics.split(",") if t.strip()]
            st.rerun()

if st.sidebar.button("🗑️ Clear Everything"):
    st.session_state.syllabus = {}
    st.session_state.logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
    st.session_state.done = []
    st.rerun()

# --- 4. MAIN INTERFACE ---
st.title("🛡️ CA Foundation Command Center")

# --- SYLLABUS SECTION ---
st.header("📊 Syllabus & Progress")
if not st.session_state.syllabus:
    st.info("Your syllabus is empty. Use the sidebar to add subjects!")
else:
    cols = st.columns(len(st.session_state.syllabus))
    for i, (sub, topics) in enumerate(st.session_state.syllabus.items()):
        with cols[i]:
            st.subheader(sub)
            for t in topics:
                # Unique key for every checkbox to prevent errors
                key = f"chk_{sub}_{t}"
                checked = st.checkbox(t, value=(t in st.session_state.done), key=key)
                
                if checked and t not in st.session_state.done:
                    st.session_state.done.append(t)
                elif not checked and t in st.session_state.done:
                    st.session_state.done.remove(t)
            
            # Subject Progress Calculation
            done_count = len([t for t in topics if t in st.session_state.done])
            total = len(topics)
            prog = done_count/total if total > 0 else 0
            st.progress(prog)
            st.caption(f"{int(prog*100)}% Finished")

st.divider()

# --- LOGGING & CALENDAR SECTION ---
col_a, col_b = st.columns([1, 2])

with col_a:
    st.header("📝 Log Study")
    with st.form("study_log", clear_on_submit=True):
        d = st.date_input("Date", date.today())
        s = st.selectbox("Subject", list(st.session_state.syllabus.keys()) if st.session_state.syllabus else ["Add a subject first"])
        tp = st.text_input("Topic")
        h = st.number_input("Hours", min_value=0.5, step=0.5)
        
        if st.form_submit_button("Record Session"):
            if st.session_state.syllabus:
                new_entry = pd.DataFrame([[d, s, tp, h]], columns=["Date", "Subject", "Topic", "Hours"])
                st.session_state.logs = pd.concat([st.session_state.logs, new_entry], ignore_index=True)
                st.rerun()

with col_b:
    st.header("📅 Study History")
    if not st.session_state.logs.empty:
        st.dataframe(st.session_state.logs.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)
        
        # Analysis Graph
        fig = px.bar(st.session_state.logs, x="Date", y="Hours", color="Subject", title="Weekly Study Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No logs yet. Start studying!")
