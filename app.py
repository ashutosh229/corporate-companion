import streamlit as st

if "chat_history" not in st.session_stat:
    st.session_state.chat_history = []
if 'current_task' not in st.session_state:
    st.session_state.current_task = "intro"
if 'user_info_collected' not in st.session_state:
    st.session_state.user_info_collected = False
if 'upload_resume' not in st.session_state:
    st.session_state.upload_resume = False