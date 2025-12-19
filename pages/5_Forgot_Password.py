# ==============================================================================
# PASSWORD RECOVERY PAGE
# ==============================================================================

# This Streamlit page provides a secure password and username recovery mechanism
# for users who are not authenticated.

# Scope of responsibility:
# - allow users to reset their password using recovery credentials
# - allow users to recover their username using email and recovery code
# - validate user input before executing sensitive operations
# - ensure no authenticated session is required

# Security considerations:
# - page is accessible without authentication
# - sidebar and navigation are fully hidden
# - no user data is exposed without successful verification
# - recovery can be performed using recovery code OR license key

# Architectural role:
# - public authentication support page
# - interacts with user data and security layers
# - contains no persistent session state changes

import streamlit as st

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================

# Use a centered layout to focus user attention
# on the recovery process and minimise distractions.
st.set_page_config(
    page_title="Password Recovery",
    page_icon="🔑",
    layout="centered"
)

# ==============================================================================
# DEPENDENCIES AND UI HARDENING
# ==============================================================================

# Import user recovery functions.
from app.data.users import (
    get_user_by_username_for_recovery,
    reset_password_with_recovery,
    generate_recovery_code_for_user
)

# Import UI utility to fully hide sidebar.
from app.utils.navigation import hide_sidebar_completely

# Hide sidebar completely because this page
# must not expose any authenticated navigation.
hide_sidebar_completely()

# ==============================================================================
# PAGE HEADER
# ==============================================================================

st.title("🔑 Password Recovery")
st.markdown("---")

# ==============================================================================
# RECOVERY MODES (TABS)
# ==============================================================================

# The page is divided into two independent recovery paths:
# 1. Password reset
# 2. Username recovery
tab1, tab2 = st.tabs(["Reset Password", "Forgot Username"])

# ==============================================================================
# TAB 1: PASSWORD RESET
# ==============================================================================

with tab1:
    st.subheader("Reset Your Password")

    # Explain required credentials clearly to the user.
    st.info(
        "You need your username, email, and either a recovery code "
        "or your license key."
    )

    # Use a form to ensure controlled submission
    # and avoid partial processing.
    with st.form("reset_password_form"):
        username = st.text_input(
            "Username",
            placeholder="Enter your username"
        )
        email = st.text_input(
            "Email",
            placeholder="Enter your email address"
        )
        recovery_input = st.text_input(
            "Recovery Code or License Key",
            placeholder="Enter recovery code or license key",
            help="You can use either your recovery code or license key"
        )
        new_password = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password"
        )
        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            placeholder="Confirm new password"
        )

        submit_button = st.form_submit_button(
            "Reset Password",
            width='stretch'
        )

        if submit_button:
            # Import email validation here to avoid circular imports.
            from app.data.security import is_valid_email

            # Basic input validation before touching database logic.
            if not all([
                username,
                email,
                recovery_input,
                new_password,
                confirm_password
            ]):
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                # Execute secure password reset workflow.
                success, message = reset_password_with_recovery(
                    username,
                    email,
                    recovery_input,
                    new_password
                )

                if success:
                    st.success(message)
                    st.info("You can now login with your new password.")

                    # Explicit navigation back to login page.
                    if st.button("Go to Login"):
                        st.switch_page("Home.py")
                else:
                    # Display either validation messages or a single error.
                    if isinstance(message, list):
                        for error in message:
                            st.error(error)
                    else:
                        st.error(message)

# ==============================================================================
# TAB 2: USERNAME RECOVERY
# ==============================================================================

with tab2:
    st.subheader("Recover Your Username")

    st.info(
        "Enter your email and recovery code to retrieve your username."
    )

    with st.form("forgot_username_form"):
        email = st.text_input(
            "Email",
            placeholder="Enter your email address"
        )
        recovery_code = st.text_input(
            "Recovery Code",
            placeholder="Enter your recovery code"
        )

        submit_button = st.form_submit_button(
            "Recover Username",
            width='stretch'
        )

        if submit_button:
            # Import email validation here to avoid circular imports.
            from app.data.security import is_valid_email

            if not email or not recovery_code:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            else:
                # Lookup user by email.
                from app.data.users import get_user_by_email
                user = get_user_by_email(email)

                if not user:
                    st.error("No user found with this email address.")
                else:
                    # Handle both legacy and current database schemas.
                    if len(user) >= 10:
                        (
                            user_id,
                            username,
                            password_hash,
                            is_admin,
                            disabled,
                            role,
                            db_email,
                            license_key,
                            failed_attempts,
                            db_recovery_code
                        ) = user
                    else:
                        (
                            user_id,
                            username,
                            password_hash,
                            is_admin,
                            disabled,
                            role,
                            db_email,
                            license_key
                        ) = user
                        db_recovery_code = None

                    recovery_upper = recovery_code.upper().strip()
                    db_recovery_upper = (
                        db_recovery_code.upper().strip()
                        if db_recovery_code else ""
                    )
                    license_upper = (
                        license_key.upper().strip()
                        if license_key else ""
                    )
                    # Accept either recovery code or license key.
                    if (
                        recovery_upper == db_recovery_upper
                        or recovery_upper == license_upper
                    ):
                        st.success(
                            f"✅ Your username is: **{username}**"
                        )
                        st.info(
                            "You can now login with your username."
                        )
                    else:
                        st.error(
                            "Invalid recovery code or license key."
                        )

# ==============================================================================
# FOOTER NAVIGATION
# ==============================================================================

st.markdown("---")

# Provide a safe and explicit return path to login.
if st.button("← Back to Login"):
    st.switch_page("Home.py")
