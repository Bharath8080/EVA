import streamlit as st
import sys
import os

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db
from utils.auth import login, register_company, join_company
from utils.styling import get_theme_css

st.set_page_config(page_title="EVA: Secure Access", layout="wide", initial_sidebar_state="collapsed")
st.markdown(get_theme_css(), unsafe_allow_html=True)

def page_auth():
    conn = get_db()
    st.markdown("<h1 style='text-align: center; margin-bottom: 50px;'><i class='bi bi-shield-lock'></i> EVA: Secure Access</h1>", unsafe_allow_html=True)
    
    # Wide layout for login page as requested
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_register, tab_join = st.tabs(["Login", "Register Company", "Join Team"])
        
        with tab_login:
            email = st.text_input("Email", key="l_email")
            pwd = st.text_input("Password", type="password", key="l_pwd")
            if st.button("Login"):
                if login(conn, email, pwd):
                    st.success("Login Successful!")
                    # Redirect based on role
                    if st.session_state.user["role"] == "admin":
                        st.switch_page("pages/4_📊_Admin_Dashboard.py")
                    else:
                        st.switch_page("pages/2_💬_Chat.py")
                else:
                    st.error("Invalid Credentials")
                    
        with tab_register:
            c_name = st.text_input("Company Name")
            a_email = st.text_input("Admin Email")
            a_pwd = st.text_input("Admin Password", type="password")
            if st.button("Register Company"):
                success, msg = register_company(conn, c_name, a_email, a_pwd)
                if success: 
                    st.success("Company Registered Successfully!")
                    st.markdown("**Workspace ID (Copy this):**")
                    st.code(msg, language="text")
                    st.info("Please switch to the 'Login' tab to sign in.")
                else:
                    st.error(msg)
                    
        with tab_join:
            j_id = st.text_input("Workspace ID")
            j_email = st.text_input("Your Email")
            j_pwd = st.text_input("Password", type="password")
            if st.button("Join Team"):
                success, msg = join_company(conn, j_email, j_pwd, j_id)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

if __name__ == "__main__":
    page_auth()
