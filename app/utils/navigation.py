import streamlit as st


def hide_default_streamlit_menu():
    """
    Hide Streamlit default pages navigation.
    """
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


def hide_sidebar_completely():
    """
    Hide sidebar completely (login page).
    """
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


def render_navigation_sidebar():
    """
    Custom sidebar navigation (authenticated users only).
    """
    with st.sidebar:
        st.markdown("### 🧭 Navigation")
        st.markdown("---")

        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("Home.py")

        if st.button("👤 Users", use_container_width=True):
            st.switch_page("pages/1_Users.py")

        if st.button("🛡️ Cyber Incidents", use_container_width=True):
            st.switch_page("pages/2_Cyber_Incidents.py")

        if st.button("📊 Datasets", use_container_width=True):
            st.switch_page("pages/3_Datasets.py")

        if st.button("🎫 IT Tickets", use_container_width=True):
            st.switch_page("pages/4_IT_Tickets.py")

        # ======================
        # 🤖 AI CHAT MODULE
        # ======================
        st.markdown("---")

        if st.button("🤖 AI Assistant", use_container_width=True):
            st.switch_page("pages/6_AI_Assistant.py")

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            from app.utils.auth import logout
            logout()
