import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

from app.data.users import (
    get_all_users,
    create_user_secure,
    delete_user,
    get_user_by_id,
)
from app.utils.auth import require_login

# Check if user is logged in
user = require_login()

st.title("👤 Users Management")

# Display current user info
col1, col2 = st.columns([3, 1])
with col1:
    st.caption(f"Logged in as: **{user['username']}** ({user['role']})")
with col2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

# Tabs
tab_view, tab_add, tab_delete = st.tabs(["View Users", "Add User", "Delete User"])

# =======================
# VIEW USERS
# =======================
with tab_view:
    st.subheader("All Users")
    users = get_all_users()
    df = pd.DataFrame(
        users,
        columns=[
            "id",
            "username",
            "password_hash",
            "is_admin",
            "disabled",
            "role",
            "email",
            "license_key",
        ],
    )
    st.dataframe(df, use_container_width=True)

# =======================
# ADD USER (IMPROVED)
# =======================
with tab_add:
    st.subheader("Add New User")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["user", "admin"])
    
    if st.button("Create User"):
        if not username or not password:
            st.error("Username and password are required.")
        else:
            # Use create_user_secure which handles password validation and hashing
            is_admin = 1 if role == "admin" else 0
            disabled = 0
            
            success, message = create_user_secure(
                username,
                password,
                is_admin,
                disabled,
                role,
                email,
            )
            
            if success:
                st.success(message)
            else:
                # message is a list of error messages
                if isinstance(message, list):
                    for error in message:
                        st.error(error)
                else:
                    st.error(message)

# =======================
# DELETE USER
# =======================
with tab_delete:
    st.subheader("Delete User by ID")
    user_id = st.number_input("User ID", min_value=1, step=1)
    if st.button("Delete"):
        user = get_user_by_id(int(user_id))
        if not user:
            st.error("User not found.")
        else:
            success, message = delete_user(int(user_id))
            if success:
                st.success(message)
            else:
                st.error(message)

