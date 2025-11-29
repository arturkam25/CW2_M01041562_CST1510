import streamlit as st


def require_login():
    """
    Check if user is authenticated. If not, redirect to login.
    Call this at the beginning of protected pages.
    """
    if "authenticated" not in st.session_state or not st.session_state.authenticated:
        st.warning("Please log in to access this page.")
        st.info("Redirecting to login page...")
        st.switch_page("pages/0_Login.py")
        st.stop()
    
    return st.session_state.user


def require_admin():
    """
    Check if user is authenticated and is an admin.
    Call this at the beginning of admin-only pages.
    """
    user = require_login()
    
    if not user.get("is_admin", False):
        st.error("Access denied. Admin privileges required.")
        st.stop()
    
    return user


def get_current_user():
    """
    Get current logged-in user data.
    Returns None if not logged in.
    """
    if "authenticated" in st.session_state and st.session_state.authenticated:
        return st.session_state.user
    return None


def is_logged_in():
    """
    Check if user is currently logged in.
    """
    return st.session_state.get("authenticated", False)

