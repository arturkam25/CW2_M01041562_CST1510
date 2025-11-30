import streamlit as st

st.set_page_config(
    page_title="Password Recovery",
    page_icon="🔑",
    layout="centered"
)

from app.data.users import get_user_by_username_for_recovery, reset_password_with_recovery, generate_recovery_code_for_user
# Import security functions inside functions to avoid circular import

st.title("🔑 Password Recovery")
st.markdown("---")

# Tabs for different recovery methods
tab1, tab2 = st.tabs(["Reset Password", "Forgot Username"])

with tab1:
    st.subheader("Reset Your Password")
    st.info("You need your username, email, and either recovery code or license key.")
    
    with st.form("reset_password_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        email = st.text_input("Email", placeholder="Enter your email address")
        recovery_input = st.text_input("Recovery Code or License Key", placeholder="Enter recovery code or license key", help="You can use either your recovery code or license key")
        new_password = st.text_input("New Password", type="password", placeholder="Enter new password")
        confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Confirm new password")
        
        submit_button = st.form_submit_button("Reset Password", use_container_width=True)
        
        if submit_button:
            # Import here to avoid circular import
            from app.data.security import is_valid_email
            if not all([username, email, recovery_input, new_password, confirm_password]):
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            elif new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = reset_password_with_recovery(username, email, recovery_input, new_password)
                
                if success:
                    st.success(message)
                    st.info("You can now login with your new password.")
                    if st.button("Go to Login"):
                        st.switch_page("pages/0_Login.py")
                else:
                    if isinstance(message, list):
                        for error in message:
                            st.error(error)
                    else:
                        st.error(message)

with tab2:
    st.subheader("Recover Your Username")
    st.info("Enter your email and recovery code to retrieve your username.")
    
    with st.form("forgot_username_form"):
        email = st.text_input("Email", placeholder="Enter your email address")
        recovery_code = st.text_input("Recovery Code", placeholder="Enter your recovery code")
        
        submit_button = st.form_submit_button("Recover Username", use_container_width=True)
        
        if submit_button:
            # Import here to avoid circular import
            from app.data.security import is_valid_email
            if not email or not recovery_code:
                st.error("Please fill in all fields.")
            elif not is_valid_email(email):
                st.error("Invalid email format.")
            else:
                from app.data.users import get_user_by_email
                user = get_user_by_email(email)
                
                if not user:
                    st.error("No user found with this email address.")
                else:
                    # Handle old and new schema
                    if len(user) >= 10:
                        user_id, username, password_hash, is_admin, disabled, role, db_email, license_key, failed_attempts, db_recovery_code = user
                    else:
                        user_id, username, password_hash, is_admin, disabled, role, db_email, license_key = user
                        db_recovery_code = None
                    
                    recovery_upper = recovery_code.upper().strip()
                    db_recovery_upper = db_recovery_code.upper().strip() if db_recovery_code else ""
                    license_upper = license_key.upper().strip() if license_key else ""
                    
                    if recovery_upper == db_recovery_upper or recovery_upper == license_upper:
                        st.success(f"✅ Your username is: **{username}**")
                        st.info("You can now login with your username.")
                    else:
                        st.error("Invalid recovery code or license key.")

st.markdown("---")
if st.button("← Back to Login"):
    st.switch_page("pages/0_Login.py")

