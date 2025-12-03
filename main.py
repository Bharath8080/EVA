import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# Initialize session state
if "page" not in st.session_state: st.session_state.page = "auth"
if "user" not in st.session_state: st.session_state.user = None
if "auth_status" not in st.session_state: st.session_state.auth_status = False
if "theme" not in st.session_state: st.session_state.theme = "dark" 

# Main entry point logic
def main():
    # If not authenticated, redirect to login
    if not st.session_state.get("auth_status"):
        st.switch_page("pages/1_🔐_Login.py")
    else:
        # Default to Chat page if logged in
        st.switch_page("pages/2_💬_Chat.py")

if __name__ == "__main__":
    main()
