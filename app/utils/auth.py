# ==============================================================================
# STREAMLIT AUTHENTICATION GUARDS AND SESSION CONTROL
# ==============================================================================

# This file provides access control helpers
# for Streamlit pages within the application.

# Scope of responsibility:
# - blocking access to protected pages for unauthenticated users
# - enforcing admin-only access where required
# - handling user logout and session cleanup

# Architectural role:
# - UI-level security guard
# - tightly coupled to Streamlit session_state
# - used by pages and navigation components

# Design notes:
# - access control is enforced at page level
# - unauthorised access stops page execution immediately
# - logout always redirects the user to the Home page

import streamlit as st

# ==============================================================================
# AUTHENTICATION GUARD
# ==============================================================================

# This section contains helpers that enforce
# user authentication for protected pages.

def require_login():
    # Blocks access to the current page
    # if the user is not authenticated.
    
    # Behaviour:
    # - shows a warning message
    # - stops further page execution
    # - returns the authenticated user object
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.stop()

    return st.session_state.user

# ==============================================================================
# ADMIN ACCESS GUARD
# ==============================================================================

# This section enforces admin-only access
# on selected pages or actions.

def require_admin():
    # Blocks access if the current user
    # does not have administrative privileges.
    user = require_login()

    if not user.get("is_admin", False):
        st.error("Access denied. Admin privileges required.")
        st.stop()

    return user

# ==============================================================================
# LOGOUT HANDLING
# ==============================================================================

# This section handles user logout
# and session cleanup.

def logout():
    # Logs the user out by clearing session state
    # and redirecting to the Home page.
    st.session_state.authenticated = False
    st.session_state.user = None
    st.switch_page("Home.py")
