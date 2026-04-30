
import streamlit as st
import pandas as pd
from datetime import date
import time
import plotly.express as px

# --- APP CONFIG ---
st.set_page_config(page_title="CA Journey Tracker", layout="wide", page_icon="🎓")

# --- CRITICAL: INITIALIZE STORAGE (Prevents AttributeErrors) ---
if 'custom_syllabus' not in st.session_state:
    st.session_state.custom_syllabus = {}
if 'study_logs' not in st.session_state:
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
if 'completed_topics' not in st.session_state:
    st.session_state.completed_topics = []

# --- SIDEBAR SETUP ---
st.sidebar.header("⚙️ App Setup")

with st.sidebar.expander("➕ Add New Subject"):
    new_sub = st.text_input("Subject Name (e.g., Law)")
    new_topics_raw = st.text_area("Topics (Separate by commas)")
    if st.button("Save Subject"):
        if new_sub and new_topics_raw:
            # Clean up the list of topics
            topic_list = [t.strip() for t in new_topics_raw.split(",") if t.strip()]
            st.session_state.custom_syllabus[new_sub] = topic_list
            st.success(f"Added {new_sub}!")
            st.rerun()

if st.sidebar.button("🗑️ Reset All Data"):
    st.session_state.custom_syllabus = {}
    st.session_state.study_logs = pd.DataFrame(columns=["Date", "Subject", "Topic", "Hours"])
    st.session_state.completed_topics = []
    st.rerun()

# --- MAIN DASHBOARD ---
st.title("🛡️ CA Foundation Command Center")

# --- 1. SYLLABUS PROGRESS ---
st.subheader("📊 Syllabus Completion")
if not st.session_state.custom_syllabus:
    st.info("Start by adding your subjects in the sidebar! 👈")
else:
    # Creating a dynamic grid
    subs = list(st.session_state.custom_syllabus.keys())
    cols = st.columns(len(subs))
    
    for i, sub in enumerate(subs):
        with cols[i]:
            st.markdown(f"### {sub}")
            topics = st.session_state.custom_syllabus[sub]
            
            for t in topics:
                # Use a unique key for each checkbox
                unique_key = f"check_{sub}_{t}"
                is_checked = t in st.session_state.completed_topics
                
                if st.checkbox(t, value=is_checked, key=unique_key):
                    if t not in st.session_state.completed_topics:
                        st.session_state.completed_topics.append(t)
                else:
                    if t in st.session_state.completed_topics:
                        st.session_state.completed_topics.remove(t)
            
            # Progress bar for this subject
            done_count = len([t for t in topics if t in st.session_state.completed_topics])
            total_count = len(topics)
            if total_count > 0:
                prog = done_count / total_count
                st.progress(prog)
                st.caption(f"{int(prog*100)}% complete")

# --- 2. THE CALENDAR & LOGS ---
st.divider()
col_log, col_cal = st.columns([1, 2])

with col_log:
    st.write("#### 📝 Record Session")
    with st.form("log_form", clear_on_submit=True):
        l_date = st.date_input("Date", date.today())
        # Safety check for the selectbox
        l_sub = st.selectbox("Subject", subs if subs else ["None"])
        l_topic = st.text_input("What did you study?")
        l_hrs = st.number_input("Hours", min_value=0.1, step=0.5)
        
        if st.form_submit_button("Save Entry"):
            if subs:
                new_row = pd.DataFrame([[l_date, l_sub, l_topic, l_hrs]], 
                                       columns=["Date", "Subject", "Topic", "Hours"])
                st.session_state.study_logs = pd.concat([st.session_state.study_logs, new_row], ignore_index=True)
                st.rerun()

with col_cal:
    st.write("#### 📅 Study History")
    if not st.session_state.study_logs.empty:
        # Sort by most recent date
        display_df = st.session_state.study_logs.sort_values(by="Date", ascending=False)
        st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.write("No study sessions logged yet.")

# --- 3. ANALYSIS ---
if not st.session_state.study_logs.empty:
    st.divider()
    st.write("### 📈 Time Analysis")
    fig = px.pie(st.session_state.study_logs, values='Hours', names='Subject', hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

# --- BACKUP ---
st.sidebar.divider()
if not st.session_state.study_logs.empty:
    csv = st.session_state.study_logs.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button("📥 Download CSV Backup", data=csv, file_name="ca_study_data.csv")
