import streamlit as st
import pandas as pd
from datetime import date
import time
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="My CA Journey Tracker", layout="wide", page_icon="🎓")

# --- INITIALIZE DATA STORAGE ---
# This holds your custom subjects and topics
if 'custom_syllabus' not in st.session_state:
    st.session_state.custom_syllabus = {}
# This holds your study logs
if 'study_logs' not in st.session_state:
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
# This holds what is finished
if 'completed_topics' not in st.session_state:
    st.session_state.completed_topics = []

# --- SIDEBAR: APP SETTINGS (Customization) ---
st.sidebar.header("⚙️ App Setup")
st.sidebar.info("Use this to set your Foundation/Inter/Final subjects.")

with st.sidebar.expander("➕ Add/Edit Subjects"):
    new_sub = st.text_input("Subject Name (e.g. Accounts)")
    new_topics = st.text_area("Topics (Separate by commas)").split(",")
    if st.button("Save Subject"):
        if new_sub and new_topics:
            st.session_state.custom_syllabus[new_sub] = [t.strip() for t in new_topics]
            st.success(f"Added {new_sub}!")

if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.custom_syllabus = {}
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
    st.session_state.completed_topics = []
    st.rerun()

# --- MAIN INTERFACE ---
st.title("🛡️ CA Command Center")

# --- 1. SYLLABUS TRACKER ---
st.subheader("📊 Syllabus Progress")
if not st.session_state.custom_syllabus:
    st.warning("Please add subjects in the sidebar to start!")
else:
    cols = st.columns(len(st.session_state.custom_syllabus))
    for i, (sub, topics) in enumerate(st.session_state.custom_syllabus.items()):
        with cols[i]:
            st.markdown(f"### {sub}")
            for t in topics:
                is_done = t in st.session_state.completed_topics
                if st.checkbox(t, value=is_done, key=f"chk_{sub}_{t}"):
                    if t not in st.session_state.completed_topics:
                        st.session_state.completed_topics.append(t)
                elif t in st.session_state.completed_topics:
                    st.session_state.completed_topics.remove(t)
            
            # Sub-progress
            sub_total = len(topics)
            sub_done = len([t for t in topics if t in st.session_state.completed_topics])
            st.progress(sub_done/sub_total if sub_total > 0 else 0)
            st.caption(f"{sub_done}/{sub_total} Topics")

# --- 2. THE CALENDAR & RECORDING ---
st.divider()
st.subheader("📅 Study Calendar & Logger")
col_log, col_cal = st.columns([1, 2])

with col_log:
    st.write("#### Record Study Session")
    with st.form("study_form", clear_on_submit=True):
        log_date = st.date_input("Date", date.today())
        log_sub = st.selectbox("Subject", list(st.session_state.custom_syllabus.keys()))
        log_topic = st.text_input("Specific Topic Studied")
        log_hrs = st.number_input("Hours", min_value=0.5, step=0.5)
        
        if st.form_submit_button("Log Session"):
            new_entry = pd.DataFrame([[log_date, log_sub, log_topic, log_hrs]], 
                                     columns=["Date", "Subject", "Topic", "Hours"])
            st.session_state.study_logs = pd.concat([st.session_state.study_logs, new_entry], ignore_index=True)
            st.success("Session Recorded!")

with col_cal:
    st.write("#### Your Recorded Journey")
    if not st.session_state.study_logs.empty:
        # We use a dataframe to act as a 'Calendar List'
        cal_df = st.session_state.study_logs.sort_values(by="Date", ascending=False)
        st.dataframe(cal_df, use_container_width=True, hide_index=True)
    else:
        st.info("Your study history will appear here.")

# --- 3. ANALYSIS ---
st.divider()
if not st.session_state.study_logs.empty:
    st.write("### 📈 Time Analysis")
    fig = px.pie(st.session_state.study_logs, values='Hours', names='Subject', title='Distribution of Study Time')
    st.plotly_chart(fig, use_container_width=True)

# --- CSV BACKUP ---
st.sidebar.divider()
if not st.session_state.study_logs.empty:
    csv = st.session_state.study_logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download My Data", data=csv, file_name="my_ca_journey.csv")
