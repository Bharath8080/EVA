"""Authentication utilities for EVA application."""
import streamlit as st
import bcrypt
import random
import string
import datetime


def generate_id(name):
    """Generate a unique company ID from company name."""
    prefix = name[:3].upper()
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}_{suffix}"


def register_company(conn, name, email, password):
    """Register a new company with admin user."""
    c = conn.cursor()
    if c.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone():
        return False, "Email exists."
    
    cid = generate_id(name)
    try:
        c.execute("INSERT INTO companies (company_id, name, created_at, admin) VALUES (?, ?, ?, ?)",
                  (cid, name, datetime.datetime.now().isoformat(), email))
        
        c.execute("INSERT INTO users (email, password, role, company_id, company_name) VALUES (?, ?, ?, ?, ?)",
                  (email, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), "admin", cid, name))
        conn.commit()
        return True, cid
    except Exception as e:
        return False, str(e)


def join_company(conn, email, password, cid):
    """Join an existing company as employee."""
    c = conn.cursor()
    company = c.execute("SELECT * FROM companies WHERE company_id = ?", (cid,)).fetchone()
    if not company:
        return False, "Invalid ID."
    
    if c.execute("SELECT email FROM users WHERE email = ?", (email,)).fetchone():
        return False, "Email exists."
    
    try:
        c.execute("INSERT INTO users (email, password, role, company_id, company_name) VALUES (?, ?, ?, ?, ?)",
                  (email, bcrypt.hashpw(password.encode(), bcrypt.gensalt()), "employee", cid, company["name"]))
        conn.commit()
        return True, "Joined!"
    except Exception as e:
        return False, str(e)


def login(conn, email, password):
    """Authenticate user and set session state."""
    c = conn.cursor()
    user = c.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and bcrypt.checkpw(password.encode(), user["password"]):
        st.session_state.user = dict(user)
        st.session_state.auth_status = True
        return True
    return False
