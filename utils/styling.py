"""Styling utilities for EVA application."""
import re
import streamlit as st
import streamlit.components.v1 as components


def get_theme_css():
    """Get CSS for the current theme."""
    themes = {
        "dark": {
            "--background-color": "#161B22",
            "--bg-gradient-start": "#0D1117",
            "--bg-gradient-end": "#161B22",
            "--primary-text-color": "#E6EDF3",
            "--secondary-text-color": "#8B949E",
            "--accent-color": "#58A6FF",
            "--accent-color-hover": "#79C0FF",
            "--card-background-color": "rgba(33, 39, 48, 0.7)",
            "--border-color": "rgba(139, 148, 158, 0.3)",
            "--glow-color": "rgba(88, 166, 255, 0.5)"
        },
    }
    theme = themes.get(st.session_state.get("theme", "dark"), themes["dark"])
    
    return f"""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <style>
        @keyframes gradientAnimation {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        :root {{ --background-color: {theme['--background-color']}; --primary-text-color: {theme['--primary-text-color']}; --accent-color: {theme['--accent-color']}; --card-background-color: {theme['--card-background-color']}; }}
        html, body, [class*="st-"] {{ font-family: 'Poppins', sans-serif; color: var(--primary-text-color); }}
        .main {{ background: linear-gradient(-45deg, {theme['--bg-gradient-start']}, {theme['--bg-gradient-end']}); background-size: 400% 400%; animation: gradientAnimation 15s ease infinite; }}
        
        /* SIDEBAR STYLING */
        [data-testid="stSidebar"] {{ 
            background-color: var(--card-background-color); 
            backdrop-filter: blur(10px); 
            border-right: 1px solid {theme['--border-color']}; 
        }}
        
        .stButton > button {{ border: 1px solid var(--accent-color); background-color: transparent; color: var(--accent-color) !important; border-radius: 8px; }}
        .stButton > button:hover {{ background-color: var(--accent-color); color: white !important; box-shadow: 0 0 15px {theme['--glow-color']}; }}
        .stTextInput > div > div > input, .stSelectbox > div > div {{ background-color: var(--card-background-color); color: var(--primary-text-color); border: 1px solid {theme['--border-color']}; border-radius: 8px; }}
        [data-testid="stChatMessage"] {{ background: var(--card-background-color); border: 1px solid {theme['--border-color']}; border-radius: 12px; }}
    </style>
    """


def render_mermaid(code, height=400):
    """Render Mermaid.js diagram."""
    html_code = f"""
    <div id="mermaid-container" style="width: 100%; overflow-x: auto;">
        <div class="mermaid">
            {code}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'dark',
            securityLevel: 'loose',
            suppressErrorRendering: true,
        }});
    </script>
    """
    return components.html(html_code, height=height, scrolling=True)


def parse_and_display_response(response_text):
    """Parse LLM response and display text/diagrams."""
    pattern = r"```mermaid(.*?)```"
    matches = re.split(pattern, response_text, flags=re.DOTALL | re.IGNORECASE)
    if len(matches) > 1:
        for i, part in enumerate(matches):
            if i % 2 == 0:
                if part.strip(): st.markdown(part)
            else:
                clean_code = part.strip().replace("`", "")
                if clean_code:
                    st.caption("📊 Process Flow")
                    render_mermaid(clean_code)
    else:
        st.markdown(response_text)
