import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

# IMPORTANT: Hide default menu FIRST, before any other imports or code
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
hide_default_streamlit_menu()

from app.data.users import (
    get_all_users,
    create_user_secure,
    delete_user,
    get_user_by_id,
    unlock_user_account,
    reset_password_with_recovery,
)
from app.utils.auth import require_admin

# Check if user is logged in and is admin
user = require_admin()

# Render custom navigation sidebar
render_navigation_sidebar()

st.title("👤 Users Management")

# =======================
# FLASH MESSAGE (MUST BE HERE)
# =======================
if "flash_message" in st.session_state:
    if st.session_state.flash_type == "success":
        st.success(st.session_state.flash_message)
    else:
        st.error(st.session_state.flash_message)

    del st.session_state.flash_message
    del st.session_state.flash_type
# =======================

# Display current user info
st.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# Tabs
tab_view, tab_add, tab_delete, tab_manage = st.tabs(
    ["View Users", "Add User", "Delete User", "Manage Accounts"]
)

# =======================
# VIEW USERS
# =======================
with tab_view:
    st.subheader("All Users")

    if st.session_state.get("user_added", False):
        st.info("✅ User added successfully! Table updated.")
        st.session_state.user_added = False

    users = get_all_users()

    if users and len(users[0]) >= 10:
        columns = [
            "id", "username", "password_hash", "is_admin", "disabled",
            "role", "email", "license_key", "failed_attempts", "recovery_code"
        ]
    else:
        columns = [
            "id", "username", "password_hash", "is_admin", "disabled",
            "role", "email", "license_key"
        ]

    df = pd.DataFrame(users, columns=columns[:len(users[0])] if users else columns)

    if 'disabled' in df.columns and 'failed_attempts' in df.columns:
        df['status'] = df.apply(
            lambda row:
            '🔒 Locked'
            if (row['disabled'] == 1 or (row['failed_attempts'] and row['failed_attempts'] >= 3))
            else f"⚠️ {int(row['failed_attempts'])} attempts"
            if row['failed_attempts'] and row['failed_attempts'] > 0
            else '✅ Active',
            axis=1
        )

    st.dataframe(df, use_container_width=True)

# =======================
# ADD USER
# =======================
with tab_add:
    st.subheader("Add New User")

    with st.expander("ℹ️ Password Requirements", expanded=True):
        st.markdown("""
        **Password must meet all of the following requirements:**
        - At least 8 characters
        - One uppercase letter
        - One lowercase letter
        - One digit
        - One special character
        """)

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["user", "admin"])

    if st.button("Create User"):
        if not username or not password:
            st.error("Username and password are required.")
        else:
            is_admin = 1 if role == "admin" else 0

            success, message = create_user_secure(
                username,
                password,
                is_admin,
                0,
                role,
                email,
            )

            if success:
                st.session_state.user_added = True
                st.session_state.flash_message = "User created successfully."
                st.session_state.flash_type = "success"
                st.rerun()
            else:
                if isinstance(message, list):
                    for err in message:
                        st.error(err)
                else:
                    st.error(message)

# =======================
# DELETE USER
# =======================
with tab_delete:
    st.subheader("Delete User by ID")
    user_id = st.number_input("User ID", min_value=1, step=1)

    if st.button("Delete"):
        user_row = get_user_by_id(int(user_id))

        if not user_row:
            st.session_state.flash_message = "User not found."
            st.session_state.flash_type = "error"
            st.rerun()
        else:
            success, message = delete_user(int(user_id))
            st.session_state.flash_message = message
            st.session_state.flash_type = "success" if success else "error"
            st.rerun()

# =======================
# MANAGE ACCOUNTS
# =======================
with tab_manage:
    st.subheader("🔧 Account Management")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔓 Unlock Account")
        unlock_id = st.number_input("User ID to Unlock", min_value=1, step=1, key="unlock_id")

        if st.button("Unlock User"):
            success, message = unlock_user_account(int(unlock_id))
            st.session_state.flash_message = message
            st.session_state.flash_type = "success" if success else "error"
            st.rerun()

    with col2:
        st.markdown("### 🔑 Reset User Password")
        reset_id = st.number_input("User ID", min_value=1, step=1, key="reset_id")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm Password", type="password")

        if st.button("Reset Password"):
            if new_pw != confirm_pw:
                st.error("Passwords do not match.")
            else:
                from app.data.users import update_user
                user_row = get_user_by_id(int(reset_id))

                if not user_row:
                    st.error("User not found.")
                else:
                    user_id, username, _, is_admin, _, role, email, license_key = user_row[:8]
                    success, message = update_user(
                        user_id,
                        username,
                        password=new_pw,
                        is_admin=is_admin,
                        disabled=0,
                        role=role,
                        email=email,
                        license_key=license_key
                    )
                    st.session_state.flash_message = message
                    st.session_state.flash_type = "success" if success else "error"
                    st.rerun()
