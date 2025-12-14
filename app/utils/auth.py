import streamlit as st


def require_login():
    """
    Block access to protected pages if user is not logged in.
    """
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.stop()

    return st.session_state.user


def require_admin():
    """
    Block access if user is not admin.
    """
    user = require_login()

    if not user.get("is_admin", False):
        st.error("Access denied. Admin privileges required.")
        st.stop()

    return user


def logout():
    """
    Proper logout - always return to login page (Home.py).
    """
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("Home.py")
