import streamlit as st
import pandas as pd

from app.data.users import (
    get_all_users,
    create_user,
    delete_user,
    get_user_by_id,
)

st.title("👤 Users Management")

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
            import bcrypt
            import random
            import string

            # 1. Hash password automatically
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

            # 2. Generate license key automatically
            def generate_key():
                letters = string.ascii_uppercase + string.digits
                return (
                    ''.join(random.choices(letters, k=4)) + "-" +
                    ''.join(random.choices(letters, k=4)) + "-" +
                    ''.join(random.choices(letters, k=4))
                )

            license_key = generate_key()

            # 3. Role logic
            is_admin = 1 if role == "admin" else 0

            # 4. Disabled always default = 0
            disabled = 0

            try:
                new_id = create_user(
                    username,
                    password_hash,
                    is_admin,
                    disabled,
                    role,
                    email,
                    license_key,
                )
                st.success(f"User created successfully with ID {new_id}")
                st.code(f"Generated License Key: {license_key}")

            except Exception as e:
                st.error(f"Error creating user: {e}")



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
            delete_user(int(user_id))
            st.success("User deleted.")
