import streamlit as st
import sys
import os
import datetime
import re
import time
from mutagen.mp3 import MP3

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db
from utils.rag import chat_with_jarvis
from utils.audio import speak_text, transcribe_audio, autoplay_audio
from utils.styling import get_theme_css, render_mermaid
from utils.sidebar import render_sidebar

st.set_page_config(page_title="EVA: Call Mode", layout="wide", initial_sidebar_state="expanded")
st.markdown(get_theme_css(), unsafe_allow_html=True)

def page_call_mode():
    if "user" not in st.session_state or not st.session_state.user:
        st.switch_page("pages/1_🔐_Login.py")
        return

    conn = get_db()
    user = st.session_state.user
    render_sidebar()
    
    if "audio_key" not in st.session_state: st.session_state.audio_key = 0
    if "active_diagram" not in st.session_state: st.session_state.active_diagram = None
    if "processing_voice" not in st.session_state: st.session_state.processing_voice = False

    # --- ADVANCED CSS (Modal) ---
    st.markdown("""
    <style>
        .main { background: #000000 !important; } 
        .block-container { padding-top: 2rem; } 
        audio { display: none !important; }
        
        /* 1. THE MODAL CONTAINER */
        div[data-testid="stVerticalBlock"]:has(div.modal-marker) {
            position: fixed;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 70vw; max-height: 80vh;
            background-color: #0D1117; border: 1px solid #58A6FF;
            border-radius: 12px; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.9);
            z-index: 99999; padding: 20px; overflow-y: auto;
        }

        /* 2. CLOSE BUTTON STYLING (SCOPED STRICTLY TO MODAL) */
        div[data-testid="stVerticalBlock"]:has(div.modal-marker) button {
            float: right; 
            border: none; 
            background: transparent; 
            color: #ff4b4b; 
            font-size: 20px;
        }
        div[data-testid="stVerticalBlock"]:has(div.modal-marker) button:hover {
            color: #ff0000;
            background: rgba(255, 0, 0, 0.1);
            box-shadow: none;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- MODAL LOGIC ---
    modal_placeholder = st.empty()

    if st.session_state.active_diagram:
        with modal_placeholder.container():
            st.markdown('<div class="modal-marker"></div>', unsafe_allow_html=True)
            c_head, c_close = st.columns([9, 1])
            with c_head: st.markdown("### 🧠 Workflow Visualization")
            with c_close: 
                if st.button("✕", key="close_modal"):
                    st.session_state.active_diagram = None
                    st.rerun()
            st.markdown("---")
            render_mermaid(st.session_state.active_diagram, height=450)

    # --- MAIN SCREEN ---
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
    <style>
        .gradient-text {{
            background: linear-gradient(to right, #E0C3FC, #8EC5FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 3em;
            font-weight: bold;
            display: inline-block;
        }}
    </style>
    <div style='text-align: center; margin-bottom: 2rem;'>
        <span class="gradient-text">EVA VOICE ASSISTANT</span>
    </div>
    """, unsafe_allow_html=True)
        st.image("public/logo.gif", width='stretch')
        status = "🟢 LISTENING..." if not st.session_state.get("processing_voice") else "🟣 PROCESSING..."
        st.markdown(f"<p style='text-align: center; color: #888; letter-spacing: 2px;'>{status}</p>", unsafe_allow_html=True)
    
    st.write("---") 
    _, c2, _ = st.columns([2,1,2])
    with c2: 
        audio_value = st.audio_input("Tap to Speak", label_visibility="collapsed", key=f"audio_input_{st.session_state.audio_key}")

    # --- PROCESSING LOOP ---
    if audio_value:
        st.session_state.processing_voice = True
        user_text = transcribe_audio(audio_value)
        
        if user_text:
            ai_response = chat_with_jarvis(user, user_text)
            
            # --- INSTANT DIAGRAM POPUP ---
            pattern = r"```mermaid(.*?)```"
            matches = re.split(pattern, ai_response, flags=re.DOTALL | re.IGNORECASE)
            
            if len(matches) > 1:
                diagram_code = matches[1].strip()
                st.session_state.active_diagram = diagram_code
                
                with modal_placeholder.container():
                    st.markdown('<div class="modal-marker"></div>', unsafe_allow_html=True)
                    c_head, c_close = st.columns([9, 1])
                    with c_head: st.markdown("### 🧠 Workflow Visualization")
                    with c_close: st.button("✕", disabled=True) 
                    st.markdown("---")
                    render_mermaid(diagram_code, height=450)
            
            # --- AUDIO ---
            audio_fp = speak_text(ai_response)
            if audio_fp:
                audio_fp.seek(0)
                audio_meta = MP3(audio_fp)
                duration = audio_meta.info.length
                audio_fp.seek(0)
                autoplay_audio(audio_fp)
                c = conn.cursor()
                c.execute("INSERT INTO chat_history (company_id, user, query, response, timestamp, mode) VALUES (?, ?, ?, ?, ?, ?)",
                          (user["company_id"], user["email"], user_text, ai_response, datetime.datetime.now().isoformat(), "voice_call"))
                conn.commit()
                # Wait for full audio to play
                time.sleep(duration + 1)
                st.session_state.audio_key += 1
                st.rerun()
        else:
            st.warning("Could not understand audio.")
        st.session_state.processing_voice = False

if __name__ == "__main__":
    page_call_mode()
