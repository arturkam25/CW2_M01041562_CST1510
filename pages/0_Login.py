import streamlit as st

st.set_page_config(
    page_title="Login",
    page_icon="🔐",
    layout="centered"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# Display title first
st.title("🔐 Login")
st.markdown("---")

# If already logged in, show welcome message
if st.session_state.authenticated and st.session_state.user:
    st.success(f"Welcome, {st.session_state.user['username']}!")
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()
    st.stop()

# Import after title is displayed
try:
    from app.data.security import authenticate_user
except Exception as e:
    st.error(f"Error loading authentication module: {e}")
    st.code(str(e))
    st.stop()

# Login form
with st.form("login_form"):
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    submit_button = st.form_submit_button("Login", use_container_width=True)
    
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

# Footer
st.markdown("---")
st.markdown("Don't have an account? Contact your administrator.")

