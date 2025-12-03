"""Audio utilities for EVA application."""
import os
import re
import base64
import streamlit as st
from gtts import gTTS
import speech_recognition as sr
from io import BytesIO


def speak_text(text):
    """Convert text to speech using gTTS with natural English voice."""
    try:
        clean_text = re.sub(r"```.*?```", " I have displayed the diagram.", text, flags=re.DOTALL)
        # Using tld='us' for more natural American English voice
        tts = gTTS(text=clean_text, lang='en', tld='us', slow=False)
        fp = BytesIO()
        tts.write_to_fp(fp)
        return fp
    except Exception as e:
        print(f"TTS Error: {e}")
        return None


def transcribe_audio(audio_bytes):
    """Transcribe audio bytes to text using Google Speech Recognition."""
    r = sr.Recognizer()
    try:
        with open("temp_input.wav", "wb") as f: f.write(audio_bytes.read())
        with sr.AudioFile("temp_input.wav") as source:
            return r.recognize_google(r.record(source))
    except: return None


def autoplay_audio(audio_bytes):
    """Autoplay audio in Streamlit."""
    b64 = base64.b64encode(audio_bytes.read()).decode()
    md = f"""<audio autoplay="true"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
    st.markdown(md, unsafe_allow_html=True)
