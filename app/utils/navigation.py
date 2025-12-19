# ==============================================================================
# STREAMLIT UI LAYOUT AND NAVIGATION CONTROLS
# ==============================================================================

# This file provides UI-level helper functions
# related to Streamlit layout customisation
# and sidebar navigation rendering.

# Scope of responsibility:
# - hiding default Streamlit navigation elements
# - fully hiding the sidebar on selected pages
# - rendering a custom application navigation sidebar
# - handling navigation, logout and chat history actions

# Architectural role:
# - UI utility module
# - tightly coupled to Streamlit
# - used by pages to control layout and navigation behaviour

# Design notes:
# - default Streamlit navigation is disabled for full UI control
# - navigation visibility depends on authentication state
# - sidebar is the primary navigation mechanism for the app

import streamlit as st

# ==============================================================================
# STREAMLIT DEFAULT UI HIDING
# ==============================================================================

# This section contains helpers that hide
# default Streamlit UI elements.

def hide_default_streamlit_menu():
    # Hides the default Streamlit pages navigation
    # displayed in the sidebar.
    
    # This allows the application to fully control
    # navigation through custom UI components.
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# SIDEBAR VISIBILITY CONTROL
# ==============================================================================

# This section provides helpers for fully hiding
# the Streamlit sidebar when required.

def hide_sidebar_completely():
    # Completely hides the Streamlit sidebar.
    
    # Intended use:
    # - login page
    # - landing pages
    # - screens where navigation should not be visible
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ==============================================================================
# CUSTOM NAVIGATION SIDEBAR
# ==============================================================================

# This section renders the main application
# navigation sidebar for authenticated users.

def render_navigation_sidebar():
    # Renders a custom navigation sidebar.
    
    # Behaviour:
    # - visible only to authenticated users
    # - provides navigation to all main application pages
    # - allows clearing AI chat history
    # - provides logout functionality
    from app.utils.auth import require_login
    from app.services.chat_history import clear_chat_history

    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        st.markdown("---")

# ==============================================================================
# MAIN NAVIGATION
# ==============================================================================

        if st.button("🏠 Home", use_container_width=True, key="nav_home"):
            st.switch_page("Home.py")

        if st.button("👤 Users", use_container_width=True, key="nav_users"):
            st.switch_page("pages/1_Users.py")

        if st.button("🛡️ Cyber Incidents", use_container_width=True, key="nav_incidents"):
            st.switch_page("pages/2_Cyber_Incidents.py")

        if st.button("📊 Datasets", use_container_width=True, key="nav_datasets"):
            st.switch_page("pages/3_Datasets.py")

        if st.button("🎫 IT Tickets", use_container_width=True, key="nav_tickets"):
            st.switch_page("pages/4_IT_Tickets.py")

        st.markdown("---")

# ==============================================================================
# AI ASSISTANT
# ==============================================================================

        if st.button("🤖 AI Assistant", use_container_width=True, key="nav_ai"):
            st.switch_page("pages/6_AI_Assistant.py")
        # Confirmation checkbox for destructive action
        confirm_clear = st.checkbox(
            "I understand this will permanently delete my chat history",
            key="confirm_clear_chat"
        )

        if st.button(
            "🗑️ Clear chat history",
            use_container_width=True,
            disabled=not confirm_clear,
            key="clear_chat_btn"
        ):
            user = require_login()
            clear_chat_history(user["id"])
            # Clear chat history from session state to ensure UI updates immediately.
            # This prevents stale data from persisting after file deletion.
            if "chat_history" in st.session_state:
                st.session_state.chat_history = []
            st.success("Chat history cleared.")
            st.rerun()

        st.markdown("---")

# ==============================================================================
# LOGOUT (ALWAYS LAST)
# ==============================================================================
        
        if st.button("🚪 Logout", use_container_width=True, key="nav_logout"):
            from app.utils.auth import logout
            logout()
