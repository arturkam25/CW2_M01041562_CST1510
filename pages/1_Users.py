import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

from app.data.users import (
    get_all_users,
    create_user_secure,
    delete_user,
    get_user_by_id,
    unlock_user_account,
    reset_password_with_recovery,
)
from app.utils.auth import require_login, require_admin
# Import security functions inside functions to avoid circular import

# Check if user is logged in and is admin
user = require_admin()

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
tab_view, tab_add, tab_delete, tab_manage = st.tabs(["View Users", "Add User", "Delete User", "Manage Accounts"])

# =======================
# VIEW USERS
# =======================
with tab_view:
    st.subheader("All Users")
    # Show message if user was just added
    if st.session_state.get("user_added", False):
        st.info("✅ User added successfully! Table updated.")
        st.session_state.user_added = False
    users = get_all_users()
    # Handle old and new schema
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
    
    # Add status column for better visualization
    if 'disabled' in df.columns and 'failed_attempts' in df.columns:
        df['status'] = df.apply(lambda row: 
            '🔒 Locked' if (row['disabled'] == 1 or (row['failed_attempts'] and row['failed_attempts'] >= 3)) 
            else f"⚠️ {int(row['failed_attempts']) if row['failed_attempts'] else 0} attempts" if row['failed_attempts'] and row['failed_attempts'] > 0 
            else '✅ Active', axis=1)
    st.dataframe(df, use_container_width=True)

# =======================
# ADD USER (IMPROVED)
# =======================
with tab_add:
    st.subheader("Add New User")
    
    # Display password requirements
    with st.expander("ℹ️ Password Requirements", expanded=True):
        st.markdown("""
        **Password must meet all of the following requirements:**
        - ✅ At least 8 characters long
        - ✅ At least one uppercase letter (A-Z)
        - ✅ At least one lowercase letter (a-z)
        - ✅ At least one digit (0-9)
        - ✅ At least one special character (!@#$%^&*()_+-=[]{}|;':\",./<>?)
        """)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password", help="Must meet all requirements shown above")
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
                # Extract recovery code and license key from message
                if "Recovery Code:" in message:
                    lines = message.split("\n")
                    st.success(lines[0] if lines else message)
                    for line in lines[1:]:
                        if "License Key:" in line:
                            key = line.split("License Key:")[1].strip()
                            st.info(f"📋 License Key: `{key}`")
                        elif "Recovery Code:" in line:
                            code = line.split("Recovery Code:")[1].strip()
                            st.warning(f"⚠️ **IMPORTANT - Save this code!** Recovery Code: `{code}`")
                else:
                    st.success(message)
                # Mark that we need to refresh and show updated table
                st.session_state.user_added = True
                st.rerun()
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
                st.rerun()  # Automatically refresh to update table
            else:
                st.error(message)

# =======================
# MANAGE ACCOUNTS (ADMIN)
# =======================
with tab_manage:
    st.subheader("🔧 Account Management")
    
    manage_col1, manage_col2 = st.columns(2)
    
    with manage_col1:
        st.markdown("### 🔓 Unlock Account")
        unlock_user_id = st.number_input("User ID to Unlock", min_value=1, step=1, key="unlock_id")
        if st.button("Unlock User", key="unlock_btn"):
            unlock_user = get_user_by_id(int(unlock_user_id))
            if not unlock_user:
                st.error("User not found.")
            else:
                success, message = unlock_user_account(int(unlock_user_id))
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    
    with manage_col2:
        st.markdown("### 🔑 Reset User Password (Admin)")
        reset_user_id = st.number_input("User ID to Reset Password", min_value=1, step=1, key="reset_id")
        new_password_admin = st.text_input("New Password", type="password", key="reset_pw")
        confirm_password_admin = st.text_input("Confirm Password", type="password", key="reset_pw_confirm")
        
        if st.button("Reset Password", key="reset_btn"):
            if not new_password_admin or not confirm_password_admin:
                st.error("Please enter both password fields.")
            elif new_password_admin != confirm_password_admin:
                st.error("Passwords do not match.")
            else:
                # Import here to avoid circular import
                from app.data.security import validate_password_strength, password_feedback
                valid, checks = validate_password_strength(new_password_admin)
                if not valid:
                    for error in password_feedback(checks):
                        st.error(error)
                else:
                    reset_user = get_user_by_id(int(reset_user_id))
                    if not reset_user:
                        st.error("User not found.")
                    else:
                        # Get user data
                        if len(reset_user) >= 10:
                            user_id, username, password_hash, is_admin, disabled, role, email, license_key, failed_attempts, recovery_code = reset_user
                        else:
                            user_id, username, password_hash, is_admin, disabled, role, email, license_key = reset_user
                        
                        # Update password
                        from app.data.users import update_user
                        success, message = update_user(
                            int(reset_user_id),
                            username,
                            password=new_password_admin,
                            is_admin=is_admin,
                            disabled=0,  # Also unlock if locked
                            role=role,
                            email=email,
                            license_key=license_key
                        )
                        if success:
                            st.success(f"Password reset successfully for user '{username}'. Account unlocked.")
                            st.rerun()
                        else:
                            st.error(message)

