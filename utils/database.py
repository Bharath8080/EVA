"""Database utilities for EVA application."""
import streamlit as st
import sqlite3
import datetime


@st.cache_resource
def get_db():
    """Get database connection with Row factory."""
    conn = sqlite3.connect('agento.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_db()
    c = conn.cursor()
    
    # Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY, password BLOB, role TEXT, company_id TEXT, company_name TEXT)''')
    
    # Companies Table
    c.execute('''CREATE TABLE IF NOT EXISTS companies
                 (company_id TEXT PRIMARY KEY, name TEXT, created_at TIMESTAMP, admin TEXT)''')
    
    # Documents Table
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, filename TEXT, category TEXT, 
                  uploaded_by TEXT, upload_date TIMESTAMP, full_text TEXT)''')
    
    # Chat History Table
    c.execute('''CREATE TABLE IF NOT EXISTS chat_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, company_id TEXT, user TEXT, query TEXT, 
                  response TEXT, timestamp TIMESTAMP, mode TEXT)''')
    
    conn.commit()
