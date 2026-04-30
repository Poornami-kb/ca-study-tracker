import streamlit as st
import pandas as pd
import time
from datetime import date, datetime
import plotly.express as px

# --- APP CONFIGURATION ---
st.set_page_config(page_title="CA Foundation Ace", layout="wide", page_icon="📝")

# --- SYLLABUS DATA ---
SYLLABUS = {
    "Accounting": ["Theoretical Framework", "Accounting Process", "BRS", "Inventories", "Depreciation", "Final Accounts", "Partnership", "Company Accounts"],
    "Business Law": ["Indian Contract Act", "Sale of Goods Act", "Partnership Act", "LLP Act", "Companies Act", "Negotiable Instruments"],
    "Quantitative Aptitude": ["Math: Ratio/Interest/Calculus", "LR: Number Series/Direction", "Stats: Probability/Correlation"],
    "Economics": ["Nature of Economics", "Demand & Supply", "Production & Cost", "Price Determination", "National Income", "Public Finance"]
}

# --- SESSION STATE INITIALIZATION ---
if 'study_logs' not in st.session_state:
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Hours"])
if 'completed_topics' not in st.session_state:
    st.session_state.completed_topics = {sub: [] for sub in SYLLABUS}

# --- HEADER & COUNTDOWN ---
exam_date = st.sidebar.date_input("Target Exam Date", date(2026, 6, 1))
days_left = (exam_date - date.today()).days

st.title("🛡️ CA Foundation Study Command Center")
st.subheader(f"⏳ {days_left} Days Remaining Until Exams")

# --- SYLLABUS PROGRESS ---
st.write("### 📊 Syllabus Completion")
cols = st.columns(4)
total_done = 0
total_topics = sum(len(topics) for topics in SYLLABUS.values())

for i, (subject, topics) in enumerate(SYLLABUS.items()):
    with cols[i]:
        done_in_subject = len(st.session_state.completed_topics[subject])
        total_in_subject = len(topics)
        perc = (done_in_subject / total_in_subject) * 100
        st.metric(subject, f"{int(perc)}%")
        st.progress(perc / 100)
        
        # Chapter Selection
        with st.expander("Update Chapters"):
            for topic in topics:
                is_checked = topic in st.session_state.completed_topics[subject]
                if st.checkbox(topic, value=is_checked, key=f"chk_{subject}_{topic}"):
                    if topic not in st.session_state.completed_topics[subject]:
                        st.session_state.completed_topics[subject].append(topic)
                elif topic in st.session_state.completed_topics[subject]:
                    st.session_state.completed_topics[subject].remove(topic)

# --- STUDY TIMER & LOGGING ---
st.divider()
col_left, col_right = st.columns([1, 2])

with col_left:
    st.write("### ⏱️ Focus Timer")
    t_subject = st.selectbox("What are you studying?", list(SYLLABUS.keys()))
    t_duration = st.number_input("Study Session (Minutes)", min_value=1, value=45)
    
    if st.button("Start Session"):
        with st.empty():
            for i in range(t_duration * 60, 0, -1):
                mins, secs = divmod(i, 60)
                st.header(f"⏳ {mins:02d}:{secs:02d}")
                time.sleep(1)
            st.success("Session Complete! Don't forget to log it below.")
            st.balloons()

with col_right:
    st.write("### 📝 Manual Log & Analytics")
    with st.form("log_form", clear_on_submit=True):
        l_date = st.date_input("Date", date.today())
        l_sub = st.selectbox("Subject", list(SYLLABUS.keys()), key="log_sub")
        l_hrs = st.number_input("Hours Studied", min_value=0.5, max_value=16.0, step=0.5)
        if st.form_submit_button("Log Hours"):
            new_entry = pd.DataFrame([[l_date, l_sub, l_hrs]], columns=["Date", "Subject", "Hours"])
            st.session_state.study_logs = pd.concat([st.session_state.study_logs, new_entry], ignore_index=True)

    # Graph
    if not st.session_state.study_logs.empty:
        fig = px.bar(st.session_state.study_logs, x="Date", y="Hours", color="Subject", title="Your Study Consistency")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Log some hours to see your study patterns!")
