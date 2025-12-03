"""Sidebar utility for EVA application."""
import streamlit as st


def render_sidebar():
    """Render the application sidebar with navigation links."""
    user = st.session_state.get("user")
    if not user:
        return

    with st.sidebar:
        st.title(f"🏢 {user['company_name']}")
        st.markdown(f"**Agent:** {user['email']}")
        st.markdown("---")
        
        # Navigation using st.page_link
        st.page_link("pages/2_💬_Chat.py", label="Go to Chat", icon="💬")
        st.page_link("pages/3_📞_Call_Mode.py", label="AI Call Mode", icon="📞")
        
        if user['role'] == 'admin':
            st.page_link("pages/4_📊_Admin_Dashboard.py", label="Admin Dashboard", icon="📊")
            
        st.page_link("pages/5_👤_User_Profile.py", label="User Profile", icon="👤")
        
        st.markdown("---")
        if st.button("Logout", width='stretch'):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.session_state.page = "auth"
            st.rerun()
