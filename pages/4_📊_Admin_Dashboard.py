import streamlit as st
import sys
import os
import pandas as pd
import time

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db
from utils.rag import ingest_file
from utils.styling import get_theme_css
from utils.sidebar import render_sidebar

st.set_page_config(page_title="EVA: Admin", layout="wide", initial_sidebar_state="expanded")
st.markdown(get_theme_css(), unsafe_allow_html=True)

def page_admin_dashboard():
    if "user" not in st.session_state or not st.session_state.user:
        st.switch_page("pages/1_🔐_Login.py")
        return
        
    user = st.session_state.user
    if user['role'] != 'admin':
        st.error("Access Denied")
        return

    conn = get_db()
    render_sidebar()
    
    st.title("Company Command Center")
    col1, col2, col3 = st.columns(3)
    
    c = conn.cursor()
    doc_count = c.execute("SELECT COUNT(*) FROM documents WHERE company_id = ?", (user["company_id"],)).fetchone()[0]
    user_count = c.execute("SELECT COUNT(*) FROM users WHERE company_id = ?", (user["company_id"],)).fetchone()[0]
    col1.metric("Total Documents", doc_count)
    col2.metric("Team Members", user_count)
    col3.metric("System Status", "Online")
    
    st.markdown("---")
    col_upload, col_list = st.columns([1, 2])
    
    with col_upload:
        st.subheader("Upload Knowledge")
        predefined_cats = ["HR", "Engineering", "Sales", "Legal", "General"]
        selected = st.selectbox("Category", predefined_cats + ["➕ Create New"])
        cat = st.text_input("New Category:").strip() if selected == "➕ Create New" else selected
        
        tab1, tab2 = st.tabs(["📂 Files", "🌐 URL"])
        
        with tab1:
            files = st.file_uploader("Select Files", type=["pdf", "txt", "md", "docx"], accept_multiple_files=True)
            if st.button("Index Files"):
                if files and cat:
                    with st.spinner("Pushing to Qdrant..."):
                        for f in files: ingest_file(conn, f, cat, user)
                    st.success("Indexed Files!")
                    time.sleep(1)
                    st.rerun()

        with tab2:
            url = st.text_input("Enter URL:")
            if st.button("Index URL"):
                if url and cat:
                    with st.spinner("Scraping & Indexing..."):
                        from utils.rag import ingest_url
                        if ingest_url(conn, url, cat, user):
                            st.success("Indexed URL!")
                            time.sleep(1)
                            st.rerun()
                
    with col_list:
        st.subheader("Recent Uploads")
        c = conn.cursor()
        docs = c.execute("SELECT filename, category, upload_date FROM documents WHERE company_id = ? ORDER BY upload_date DESC LIMIT 10", (user["company_id"],)).fetchall()
        docs = [dict(row) for row in docs]
        if docs:
            st.dataframe(pd.DataFrame(docs), width="stretch")

if __name__ == "__main__":
    page_admin_dashboard()
