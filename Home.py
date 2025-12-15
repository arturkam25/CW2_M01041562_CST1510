import streamlit as st

from app.utils.navigation import (
    hide_sidebar_completely,
    hide_default_streamlit_menu,
    render_navigation_sidebar,
)
from app.data.users import register_user_public

st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="📊",
    layout="wide",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": None,
    },
)

# =========================
# SESSION STATE
# =========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

# =========================
# IMPORTS AFTER CONFIG
# =========================
try:
    from app.data.security import authenticate_user, is_valid_email
    from app.data.schema import create_tables
    from app.data.users import reset_password_with_recovery, get_user_by_email

    create_tables()
except Exception as e:
    st.error(f"Error loading authentication module: {e}")
    st.stop()

# ============================================================
# NOT AUTHENTICATED
# ============================================================
if not st.session_state.authenticated or not st.session_state.user:
    hide_sidebar_completely()

    # ===== FORGOT PASSWORD =====
    if st.session_state.show_forgot_password:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔑 Password / Username Recovery")
            st.markdown("---")

            if st.button("← Back to Login"):
                st.session_state.show_forgot_password = False
                st.rerun()

            tab1, tab2 = st.tabs(["Reset Password", "Forgot Username"])

            with tab1:
                with st.form("reset_password_form"):
                    username = st.text_input("Username")
                    email = st.text_input("Email")
                    recovery = st.text_input("Recovery Code or License Key")
                    new_pw = st.text_input("New Password", type="password")
                    confirm_pw = st.text_input("Confirm Password", type="password")

                    submit = st.form_submit_button("Reset Password", width="stretch")

                    if submit:
                        if not all([username, email, recovery, new_pw, confirm_pw]):
                            st.error("Please fill in all fields.")
                        elif new_pw != confirm_pw:
                            st.error("Passwords do not match.")
                        else:
                            success, msg = reset_password_with_recovery(
                                username, email, recovery, new_pw
                            )
                            if success:
                                st.success(msg)
                                st.session_state.show_forgot_password = False
                                st.rerun()
                            else:
                                st.error(msg)

            with tab2:
                with st.form("forgot_username_form"):
                    email = st.text_input("Email")
                    recovery = st.text_input("Recovery Code")

                    submit = st.form_submit_button("Recover Username", width="stretch")

                    if submit:
                        user = get_user_by_email(email)
                        if not user:
                            st.error("User not found.")
                        else:
                            recovery_db = user[-1]
                            license_key = user[-3]
                            if recovery.upper() in (
                                (recovery_db or "").upper(),
                                (license_key or "").upper(),
                            ):
                                st.success(f"✅ Username: **{user[1]}**")
                            else:
                                st.error("Invalid recovery code.")

    # ===== LOGIN / REGISTER =====
    else:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            col_text, col_logo = st.columns([3, 1])

            with col_text:
                st.markdown("### 2025-26 CST1510 Programming for Data Communication and Networks")
                st.markdown("**CW2 Multi-Domain Intelligence Platform**")
                st.markdown("Artur Krzysztof Kamerski (M01041562)")

            with col_logo:
                try:
                    st.image("static/middlesex_logo.png", width=160)
                except:
                    pass

            st.markdown("---")
            st.title("🔐 Authentication")
            st.markdown("---")

            tab_login, tab_register = st.tabs(["Login", "Register"])

            # ================= LOGIN =================
            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login", width="stretch")

                    if submit:
                        success, user_data, msg = authenticate_user(username, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user = user_data
                            st.rerun()
                        else:
                            st.error(msg)

            # ================= REGISTER =================
            with tab_register:
                with st.form("register_form"):
                    new_username = st.text_input("Username")
                    new_email = st.text_input("Email")

                    with st.expander("ℹ️ Password Requirements", expanded=True):
                        st.markdown(
                            """
                            **Password must include:**
                            - At least 8 characters  
                            - Uppercase letter  
                            - Lowercase letter  
                            - Digit  
                            - Special character  
                            """
                        )

                    new_password = st.text_input("Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")

                    submit = st.form_submit_button("Create account", width="stretch")

                    if submit:
                        if not all([new_username, new_email, new_password, confirm_password]):
                            st.error("Please fill in all fields.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            success, msg = register_user_public(
                                new_username, new_password, new_email
                            )
                            if success:
                                st.success("Account created successfully")
                                st.warning(
                                    "⚠️ Save your License Key now. It will not be shown again."
                                )
                                st.code(msg)
                            else:
                                st.error(msg)

            st.markdown("---")
            if st.button("🔑 Forgot Password / Username?", width="stretch"):
                st.session_state.show_forgot_password = True
                st.rerun()

# ============================================================
# AUTHENTICATED
# ============================================================
else:
    hide_default_streamlit_menu()
    render_navigation_sidebar()

    col_title, col_logo = st.columns([3, 1])
    with col_title:
        st.title("📊 Multi-Domain Intelligence Platform")
    with col_logo:
        try:
            st.image("static/middlesex_logo.png", width=150)
        except:
            pass

    st.markdown("---")
    st.success(
        f"Welcome, **{st.session_state.user['username']}** ({st.session_state.user['role']})"
    )
    st.info("💡 Use the left sidebar to navigate between modules.")
