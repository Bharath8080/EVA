import streamlit as st
import sys
import os
import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db
from utils.rag import chat_with_jarvis
from utils.styling import get_theme_css, parse_and_display_response
from utils.sidebar import render_sidebar

st.set_page_config(page_title="EVA: Chat", layout="centered", initial_sidebar_state="expanded")
st.markdown(get_theme_css(), unsafe_allow_html=True)

def page_chat():
    if "user" not in st.session_state or not st.session_state.user:
        st.switch_page("pages/1_🔐_Login.py")
        return

    conn = get_db()
    user = st.session_state.user
    render_sidebar()
    
    st.markdown("<h1 style='text-align: center; padding-top: 20px;'>EVA AI Assistant</h1>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): 
            if msg["role"] == "assistant":
                parse_and_display_response(msg["content"])
            else:
                st.markdown(msg["content"])
                
    if prompt := st.chat_input("How can I help you?"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Thinking..."):
            response = chat_with_jarvis(user, prompt)
            
        with st.chat_message("assistant"):
            parse_and_display_response(response)
            
        st.session_state.messages.append({"role": "assistant", "content": response})

        c = conn.cursor()
        c.execute("INSERT INTO chat_history (company_id, user, query, response, timestamp, mode) VALUES (?, ?, ?, ?, ?, ?)",
                  (user["company_id"], user["email"], prompt, response, datetime.datetime.now().isoformat(), "text"))
        conn.commit()

if __name__ == "__main__":
    page_chat()
