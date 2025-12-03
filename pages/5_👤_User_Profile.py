import streamlit as st
import sys
import os
import datetime

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db
from utils.styling import get_theme_css
from utils.sidebar import render_sidebar

st.set_page_config(page_title="EVA: Profile", layout="wide", initial_sidebar_state="expanded")
st.markdown(get_theme_css(), unsafe_allow_html=True)

def page_user_profile():
    if "user" not in st.session_state or not st.session_state.user:
        st.switch_page("pages/1_🔐_Login.py")
        return

    conn = get_db()
    user = st.session_state.user
    render_sidebar()
    
    st.markdown("<h1 style='text-align: center; margin-bottom: 40px;'>User Profile</h1>", unsafe_allow_html=True)
    
    # Fetch fresh company data
    c = conn.cursor()
    company_data = c.execute("SELECT * FROM companies WHERE company_id = ?", (user["company_id"],)).fetchone()
    company_data = dict(company_data) if company_data else {}
    
    # --- LAYOUT GRID ---
    col1, col2 = st.columns([1, 1], gap="large")
    
    # --- LEFT COLUMN: PERSONAL INFO ---
    with col1:
        st.markdown("### 👤 Personal Identity")
        st.markdown(f"""
        <div style="
            background-color: rgba(22, 27, 34, 0.8); 
            padding: 25px; 
            border-radius: 15px; 
            border: 1px solid #30363d;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        ">
            <p style="font-size: 1.1rem; margin-bottom: 10px;"><strong>Email:</strong> <span style="color: #58A6FF;">{user['email']}</span></p>
            <p style="font-size: 1.1rem; margin-bottom: 10px;"><strong>Role:</strong> {user['role'].upper()}</p>
            <p style="font-size: 1.1rem; margin-bottom: 0px;"><strong>Status:</strong> <span style="color: #238636;">● Active</span></p>
        </div>
        """, unsafe_allow_html=True)

    # --- RIGHT COLUMN: COMPANY INFO ---
    with col2:
        if user['role'] == 'admin':
            st.markdown("### 🏢 Company Registry")
            
            created_at = company_data.get('created_at')
            if isinstance(created_at, str):
                try: created_at = datetime.datetime.fromisoformat(created_at)
                except: created_at = datetime.datetime.now()
            elif not isinstance(created_at, datetime.datetime):
                created_at = datetime.datetime.now()
                
            reg_date = created_at.strftime("%B %d, %Y")
            
            st.markdown(f"""
            <div style="
                background-color: rgba(22, 27, 34, 0.8); 
                padding: 25px; 
                border-radius: 15px; 
                border: 1px solid #58A6FF;
                box-shadow: 0 0 20px rgba(88, 166, 255, 0.1);
            ">
                <p style="font-size: 1.2rem; font-weight: bold; color: #E6EDF3;">{company_data['name']}</p>
                <hr style="border-color: #30363d; margin: 10px 0;">
                <p style="margin-bottom: 8px;"><strong>Registered On:</strong> {reg_date}</p>
                <p style="margin-bottom: 8px;"><strong>Admin:</strong> {company_data['admin']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.markdown("#### 🔑 Workspace Access Key")
            st.caption("Share this ID with your employees so they can join your workspace:")
            st.code(user['company_id'], language="text")
            
        else:
            st.markdown("### 🏢 Organization")
            st.markdown(f"""
            <div style="
                background-color: rgba(22, 27, 34, 0.8); 
                padding: 25px; 
                border-radius: 15px; 
                border: 1px solid #30363d;
            ">
                <p style="font-size: 1.1rem;">You are a member of:</p>
                <h2 style="color: #58A6FF; margin: 0;">{user['company_name']}</h2>
                <p style="margin-top: 10px; color: #888;">Workspace ID: {user['company_id']}</p>
            </div>
            """, unsafe_allow_html=True)

    # --- BOTTOM SECTION: ACCOUNT ACTIONS ---
    st.write("---")
    c_left, c_right = st.columns([6, 1])
    with c_right:
        if st.button("🔒 Secure Logout", type="primary", width='stretch'):
            for key in st.session_state.keys(): del st.session_state[key]
            st.session_state.page = "auth"
            st.switch_page("pages/1_🔐_Login.py")

if __name__ == "__main__":
    page_user_profile()
