from .db import get_connection
from .schema import generate_license_key
from .security import validate_password_strength, password_feedback, hash_password


def _bool(value):
    return 0 if value in (None, "None") else int(value)


def add_user_full(username, password_hash, is_admin, disabled, role, email, license_key):
    """
    Add a user to the database using INSERT OR IGNORE (prevents duplicates).
    
    Args:
        username: Unique username
        password_hash: Hashed password
        is_admin: Admin flag (0 or 1)
        disabled: Disabled flag (0 or 1)
        role: User role
        email: User email
        license_key: License key
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT OR IGNORE INTO users 
        (username, password_hash, is_admin, disabled, role, email, license_key)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        curr.execute(sql, (username, password_hash, is_admin, disabled, role, email, license_key))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def load_users_from_file(path="DATA/users.txt"):
    """
    Load users from a text file.
    
    Args:
        path: Path to the users file (default: "DATA/users.txt")
    """
    try:
        with open(path, "r") as f:
            lines = f.readlines()
        for line in lines:
            parts = line.strip().split(',')
            if len(parts) != 7:
                continue
            username, password_hash, is_admin, disabled, role, email, license_key = parts
            add_user_full(username, password_hash, is_admin, disabled, role, email, license_key)
    except FileNotFoundError:
        print(f"Warning: Users file not found at {path}")
    except Exception as e:
        print(f"Error loading users from file: {e}")


def add_test_users():
    """Add test users to the database."""
    add_user_full("alice", "hashed_password_123", None, None, None, None, None)
    add_user_full("bob", "hashed_password_456", None, None, None, None, None)


# CRUD

def create_user(username, password_hash, is_admin, disabled, role, email, license_key):
    """
    Create a new user.
    
    Args:
        username: Unique username
        password_hash: Hashed password
        is_admin: Admin flag (0 or 1)
        disabled: Disabled flag (0 or 1)
        role: User role
        email: User email
        license_key: License key
        
    Returns:
        int: The ID of the newly created user
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO users
        (username, password_hash, is_admin, disabled, role, email, license_key)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        curr.execute(sql, (username, password_hash, is_admin, disabled, role, email, license_key))
        conn.commit()
        user_id = curr.lastrowid
        return user_id
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_user_by_id(user_id):
    """
    Get a user by their ID.
    
    Args:
        user_id: The user ID
        
    Returns:
        tuple: User record or None if not found
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = curr.fetchone()
        return row
    finally:
        conn.close()


def get_user_by_username(username):
    """
    Get a user by their username.
    
    Args:
        username: The username
        
    Returns:
        tuple: User record or None if not found
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users WHERE username = ?;", (username,))
        row = curr.fetchone()
        return row
    finally:
        conn.close()


def get_all_users():
    """
    Get all users from the database.
    
    Returns:
        list: List of all user records
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users ORDER BY is_admin DESC, id ASC")
        rows = curr.fetchall()
        return rows
    finally:
        conn.close()


def update_user(user_id, username, password=None, is_admin=0, disabled=0, role="user", email="", license_key=None):
    """
    Update an existing user.
    
    Args:
        user_id: The user ID to update
        username: New username
        password: New password (optional, will be hashed if provided)
        is_admin: New admin flag
        disabled: New disabled flag
        role: New role
        email: New email
        license_key: New license key (optional)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    curr = conn.cursor()
    
    if password:
        valid, checks = validate_password_strength(password)
        if not valid:
            conn.close()
            return False, password_feedback(checks)
        password_hash = hash_password(password)
    else:
        curr.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        result = curr.fetchone()
        if not result:
            conn.close()
            return False, "User not found."
        password_hash = result[0]
    
    sql = """
        UPDATE users SET
            username = ?,
            password_hash = ?,
            is_admin = ?,
            disabled = ?,
            role = ?,
            email = ?,
            license_key = ?
        WHERE id = ?
    """
    try:
        curr.execute(sql, (
            username,
            password_hash,
            _bool(is_admin),
            _bool(disabled),
            role,
            email,
            license_key,
            user_id
        ))
        conn.commit()
        return True, "User updated."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()


def delete_user(user_id):
    """
    Delete a user by their ID.
    
    Args:
        user_id: The user ID to delete
        
    Returns:
        tuple: (success: bool, message: str)
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()
    return True, "User deleted."


# ===============================
# MAIN SECURE USER CREATION
# ===============================
def create_user_secure(username, password, is_admin, disabled, role, email):
    """
    Create a new user with password validation and hashing.
    
    Args:
        username: Unique username
        password: Plain text password (will be validated and hashed)
        is_admin: Admin flag (0 or 1)
        disabled: Disabled flag (0 or 1)
        role: User role
        email: User email
        
    Returns:
        tuple: (success: bool, message: str or list of error messages)
    """
    # 1. validate password strength
    valid, checks = validate_password_strength(password)
    if not valid:
        return False, password_feedback(checks)
    
    # 2. hash password
    password_hash = hash_password(password)
    
    license_key = generate_license_key()
    
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO users
        (username, password_hash, is_admin, disabled, role, email, license_key)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    try:
        curr.execute(sql, (
            username,
            password_hash,
            _bool(is_admin),
            _bool(disabled),
            role,
            email,
            license_key
        ))
        conn.commit()
        return True, f"User '{username}' created successfully. License: {license_key}"
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()


