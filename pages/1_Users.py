# ==============================================================================
# USERS MANAGEMENT PAGE (ADMIN)
# ==============================================================================

# This Streamlit page implements a complete administrative interface
# for managing user accounts stored in the application database.

# Scope of responsibility:
# - presenting a read-only overview of all users
# - allowing administrators to create new user accounts
# - enabling safe deletion of users
# - managing account security states (lock/unlock)
# - resetting user passwords through controlled workflows

# Access control:
# - this page is restricted to authenticated administrators
# - access is blocked immediately if the user is not an admin

# Architectural role:
# - UI controller (Streamlit page)
# - orchestrates interactions between UI components and backend services
# - contains no direct SQL or database logic

# Design philosophy:
# - all business logic lives in data or service layers
# - this page focuses purely on presentation and user interaction
# - state transitions are handled explicitly via session_state

import streamlit as st
import pandas as pd

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================

# The page uses a wide layout to accommodate large tables
# and multi-column administrative views.

st.set_page_config(layout="wide")
# IMPORTANT:
# Default Streamlit navigation must be hidden before rendering
# any UI elements to prevent UI flickering and layout conflicts.
from app.utils.navigation import hide_default_streamlit_menu, render_navigation_sidebar
hide_default_streamlit_menu()

# ==============================================================================
# DEPENDENCIES AND ACCESS CONTROL
# ==============================================================================

# Import user-related data access functions.
# No SQL or schema logic is present at page level.

from app.data.users import (
    get_all_users,
    create_user_secure,
    delete_user,
    get_user_by_id,
    unlock_user_account,
    reset_password_with_recovery,
)
# Import authentication guard enforcing admin-only access.
from app.utils.auth import require_admin
# Enforce access control immediately.
# If the user is not authenticated or not an admin,
# page execution is stopped.
user = require_admin()
# Render the custom application navigation sidebar.
# This replaces the default Streamlit page navigation.
render_navigation_sidebar()

# ==============================================================================
# PAGE HEADER AND FLASH MESSAGE HANDLING
# ==============================================================================

# Main page title.

st.title("👤 Users Management")
# Flash messages are stored in session_state to survive reruns.
# They are displayed once and then removed.
if "flash_message" in st.session_state:
    if st.session_state.flash_type == "success":
        st.success(st.session_state.flash_message)
    else:
        st.error(st.session_state.flash_message)

    del st.session_state.flash_message
    del st.session_state.flash_type
# Display context information about the currently logged-in admin.
st.caption(f"Logged in as: **{user['username']}** ({user['role']})")

# ==============================================================================
# PAGE STRUCTURE - TAB LAYOUT
# ==============================================================================

# The page is divided into logical tabs to avoid clutter
# and to separate different administrative responsibilities.

tab_view, tab_add, tab_delete, tab_manage = st.tabs(
    ["View Users", "Add User", "Delete User", "Manage Accounts"]
)

# ==============================================================================
# TAB: VIEW USERS
# ==============================================================================

# This tab provides a read-only overview of all users.
# It adapts dynamically to different database schemas
# (older vs newer versions with additional security fields).
with tab_view:
    st.subheader("All Users")
    # Informational message after successful user creation.
    if st.session_state.get("user_added", False):
        st.info("✅ User added successfully! Table updated.")
        st.session_state.user_added = False
    # Retrieve all users from the database.
    users = get_all_users()
    # Dynamically determine column layout based on schema version.
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
    # Convert raw database rows into a DataFrame for display.
    df = pd.DataFrame(users, columns=columns[:len(users[0])] if users else columns)
    # Derive a human-readable account status column.
    if "disabled" in df.columns and "failed_attempts" in df.columns:
        df["status"] = df.apply(
            lambda row:
                "🔒 Locked"
                if (row["disabled"] == 1 or (row["failed_attempts"] and row["failed_attempts"] >= 3))
                else f"⚠️ {int(row['failed_attempts'])} attempts"
                if row["failed_attempts"] and row["failed_attempts"] > 0
                else "✅ Active",
            axis=1
        )
    # Render the user table.
    st.dataframe(df, use_container_width=True)

# ==============================================================================
# TAB: ADD USER
# ==============================================================================

# This tab allows administrators to create new user accounts.
# Password strength rules are enforced before creation.

with tab_add:
    st.subheader("Add New User")
    # Password requirements are displayed explicitly
    # to prevent trial-and-error during user creation.
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
    # User creation workflow.
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

# ==============================================================================
# TAB: DELETE USER
# ==============================================================================

# This tab provides a controlled user deletion workflow.
# Deletion is performed explicitly by user ID.
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

# ==============================================================================
# TAB: ACCOUNT MANAGEMENT
# ==============================================================================

# This tab groups security-related administrative actions.
# These actions affect account state but do not remove data.
with tab_manage:
    st.subheader("🔧 Account Management")

    col1, col2 = st.columns(2)
    # Account unlock workflow.
    with col1:
        st.markdown("### 🔓 Unlock Account")

        unlock_id = st.number_input(
            "User ID to Unlock",
            min_value=1,
            step=1,
            key="unlock_id"
        )

        if st.button("Unlock User"):
            success, message = unlock_user_account(int(unlock_id))
            st.session_state.flash_message = message
            st.session_state.flash_type = "success" if success else "error"
            st.rerun()
    # Password reset workflow.
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
