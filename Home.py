import streamlit as st

# Import navigation functions at the top (but they won't be called until needed)
from app.utils.navigation import hide_sidebar_completely, hide_default_streamlit_menu, render_navigation_sidebar
from app.data.users import register_user_public



st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="📊",
    layout="wide",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_forgot_password" not in st.session_state:
    st.session_state.show_forgot_password = False

# Import after page config
try:
    from app.data.security import authenticate_user, is_valid_email
    from app.data.schema import create_tables
    from app.data.users import reset_password_with_recovery, get_user_by_email
    create_tables()
except Exception as e:
    st.error(f"Error loading authentication module: {e}")
    st.code(str(e))
    st.stop()

# If not authenticated, show login form or forgot password
if not st.session_state.authenticated or not st.session_state.user:
    # Hide sidebar completely on login page
    hide_sidebar_completely()
    # Header with logo in top right
    col_header1, col_header2 = st.columns([3, 1])
    with col_header1:
        st.write("")  # Empty space for alignment
    with col_header2:
        try:
            st.image("static/middlesex_logo.png", width=150)
        except FileNotFoundError:
            try:
                st.image("middlesex_logo.png", width=150)
            except:
                pass  # Logo not found, continue without it
        except:
            pass  # Logo not found, continue without it
    
    # Show forgot password form if requested
    if st.session_state.show_forgot_password:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.title("🔑 Password / Username Recovery")
            st.markdown("---")
            
            # Back button
            if st.button("← Back to Login"):
                st.session_state.show_forgot_password = False
                st.rerun()
            
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
                    
                    submit_button = st.form_submit_button("Reset Password", width='stretch')
                    
                    if submit_button:
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
                                st.session_state.show_forgot_password = False
                                st.rerun()
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
                    
                    submit_button = st.form_submit_button("Recover Username", width='stretch')
                    
                    if submit_button:
                        if not email or not recovery_code:
                            st.error("Please fill in all fields.")
                        elif not is_valid_email(email):
                            st.error("Invalid email format.")
                        else:
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
    else:
        # Center the login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Coursework header
            st.markdown("### 2025-26 CST1510 Programming for Data Communication and Networks")
            st.markdown("**CW2 Multi-Domain Intelligence Platform**")
            st.markdown("Artur Krzysztof Kamerski (M01041562)")
            st.markdown("---")
            
            st.title("🔐 Authentication")
            st.markdown("---")

            tab_login, tab_register = st.tabs(["Login", "Register"])

            # ================= LOGIN =================
            with tab_login:
                with st.form("login_form"):
                    username = st.text_input("Username", placeholder="Enter your username")
                    password = st.text_input("Password", type="password", placeholder="Enter your password")
                    submit_button = st.form_submit_button("Login", width='stretch')
                    
                    if submit_button:
                        if not username or not password:
                            st.error("Please enter both username and password.")
                        else:
                            success, user_data, message = authenticate_user(username, password)
                            
                            if success:
                                st.session_state.authenticated = True
                                st.session_state.user = user_data
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)

            # ================= REGISTER =================
            with tab_register:
                with st.form("register_form"):
                    new_username = st.text_input("Username", placeholder="Choose a username")
                    new_email = st.text_input("Email", placeholder="Enter your email")
                    new_password = st.text_input("Password", type="password")
                    confirm_password = st.text_input("Confirm Password", type="password")

                    submit_register = st.form_submit_button("Create account", width='stretch')

                    if submit_register:
                        if not all([new_username, new_email, new_password, confirm_password]):
                            st.error("Please fill in all fields.")
                        elif new_password != confirm_password:
                            st.error("Passwords do not match.")
                        else:
                            success, message = register_user_public(
                                new_username,
                                new_password,
                                new_email
                            )

                            if success:
                                st.success("Account created successfully")

                                st.warning(
                                    "⚠️ Save your License Key now. "
                                    "It will not be shown again."
                                )

                                st.code(message)   # <-- TU pokazujemy license_key
                            else:
                                st.error(message)




#                            success, message = register_user_public(
#                                new_username,
#                                new_password,
#                                new_email
#                            )
#
#                            if success:
#                                st.success(message)
#                                st.info("You can now log in using your credentials.")
#                            else:
#                                st.error(message)






#            st.title("🔐 Login")
#            st.markdown("---")
#            
#            # Login form
#            with st.form("login_form"):
#                username = st.text_input("Username", placeholder="Enter your username")
#                password = st.text_input("Password", type="password", placeholder="Enter your password")
#                submit_button = st.form_submit_button("Login", width='stretch')
#                
#                if submit_button:
#                    if not username or not password:
#                        st.error("Please enter both username and password.")
#                    else:
#                        success, user_data, message = authenticate_user(username, password)
#                        
#                        if success:
#                            st.session_state.authenticated = True
#                            st.session_state.user = user_data
#                            st.success(message)
#                            st.rerun()
#                        else:
#                            st.error(message)
            
            # Footer
            st.markdown("---")
            col_footer1, col_footer2 = st.columns(2)
            with col_footer1:
                if st.button("🔑 Forgot Password / Username?", width='stretch'):
                    st.session_state.show_forgot_password = True
                    st.rerun()
            with col_footer2:
                st.caption("Don't have an account? Contact your administrator.")
else:
    # User is authenticated - show main page
    
    # IMPORTANT: Hide default Streamlit menu FIRST, before rendering custom navigation
    # This prevents the default menu from flashing briefly
    hide_default_streamlit_menu()
    render_navigation_sidebar()
    
    # Header with title and logo
    col_title, col_logo = st.columns([3, 1])
    with col_title:
        st.title("📊 Multi-Domain Intelligence Platform")
    with col_logo:
        try:
            st.image("static/middlesex_logo.png", width=150)
        except FileNotFoundError:
            try:
                st.image("middlesex_logo.png", width=150)
            except:
                pass  # Logo not found, continue without it
        except:
            pass  # Logo not found, continue without it
    
    st.markdown("---")
    
    # Welcome message
    st.success(f"Welcome, **{st.session_state.user['username']}**! ({st.session_state.user['role']})")
    
    st.markdown("---")
    st.info("💡 Use the left sidebar to navigate between modules.")
