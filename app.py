
import streamlit as st
import pandas as pd
from datetime import date
import time
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="CA Foundation Tracker", layout="wide", page_icon="🎓")

# --- SYLLABUS DATA ---
SYLLABUS = {
    "Accounts": ["Accounting Process", "BRS", "Inventories", "Depreciation", "Final Accounts", "Partnership", "Company Accounts"],
    "Law": ["Contract Act", "Sale of Goods", "Partnership Act", "LLP Act", "Companies Act"],
    "QA (Math/LR/Stats)": ["Ratio & Proportion", "Time Value of Money", "Logical Reasoning", "Measures of Central Tendency", "Probability"],
    "Economics": ["Demand & Supply", "Production & Cost", "Markets", "National Income", "Public Finance"]
}

# --- INITIALIZE DATA STORAGE ---
if 'study_logs' not in st.session_state:
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Hours", "Topic"])

# --- SIDEBAR: EXAM COUNTDOWN ---
st.sidebar.header("🎯 Exam Countdown")
exam_date = st.sidebar.date_input("Exam Date", date(2024, 12, 20))
days_left = (exam_date - date.today()).days
st.sidebar.metric("Days Remaining", f"{days_left}")

# --- MAIN DASHBOARD ---
st.title("📚 CA Foundation Study Journey")

# 1. Syllabus Completion Logic
st.subheader("📊 Syllabus Progress")
cols = st.columns(4)
all_subjects_progress = []

for i, (subject, topics) in enumerate(SYLLABUS.items()):
    with cols[i]:
        st.markdown(f"**{subject}**")
        # In a real app, you'd load this from a file, for now we use checkboxes
        completed = st.multiselect(f"Done in {subject}:", topics, key=f"multi_{subject}")
        done_count = len(completed)
        total_count = len(topics)
        perc = (done_count / total_count)
        st.progress(perc)
        st.caption(f"{done_count}/{total_count} Topics Finished")
        all_subjects_progress.append(perc)

# --- 2. TIMER & MANUAL LOGGING ---
st.divider()
col_left, col_right = st.columns([1, 2])

with col_left:
    st.write("### ⏱️ Focus Timer")
    duration = st.number_input("Minutes", min_value=1, value=45)
    if st.button("Start Timer"):
        ph = st.empty()
        for i in range(duration * 60, 0, -1):
            m, s = divmod(i, 60)
            ph.header(f"⏳ {m:02d}:{s:02d}")
            time.sleep(1)
        st.success("Time Up! Log your hours now.")
        st.balloons()

with col_right:
    st.write("### 📝 Log Your Study")
    with st.form("study_form", clear_on_submit=True):
        f_date = st.date_input("Date", date.today())
        f_sub = st.selectbox("Subject", list(SYLLABUS.keys()))
        f_topic = st.text_input("What did you study?")
        f_hrs = st.number_input("Hours", min_value=0.5, max_value=16.0, step=0.5)
        
        if st.form_submit_button("Save Entry"):
            new_data = pd.DataFrame([[f_date, f_sub, f_hrs, f_topic]], 
                                    columns=["Date", "Subject", "Hours", "Topic"])
            st.session_state.study_logs = pd.concat([st.session_state.study_logs, new_data], ignore_index=True)
            st.success("Logged successfully!")

# --- 3. ANALYSIS & GRAPHS ---
st.divider()
if not st.session_state.study_logs.empty:
    st.write("### 📈 Performance Analysis")
    fig = px.bar(st.session_state.study_logs, x="Date", y="Hours", color="Subject", 
                 title="Study Hours per Day", barmode="group")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("### 📋 Recorded History")
    st.dataframe(st.session_state.study_logs, use_container_width=True)
else:
    st.info("No logs found. Start studying to see your graphs!")

# --- 4. CSV DOWNLOAD SECTION ---
st.sidebar.divider()
st.sidebar.header("💾 Backup Data")
if not st.session_state.study_logs.empty:
    csv = st.session_state.study_logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Study Log (CSV)",
        data=csv,
        file_name=f"ca_study_log_{date.today()}.csv",
        mime="text/csv",
    )
st.sidebar.caption("Tip: Download this once a week to keep a permanent backup on your laptop.")
