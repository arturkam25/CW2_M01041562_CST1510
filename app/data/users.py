from .db import get_connection


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
        curr.execute("SELECT * FROM users;")
        rows = curr.fetchall()
        return rows
    finally:
        conn.close()


def update_user(user_id, username, password_hash, is_admin, disabled, role, email, license_key):
    """
    Update an existing user.
    
    Args:
        user_id: The user ID to update
        username: New username
        password_hash: New password hash
        is_admin: New admin flag
        disabled: New disabled flag
        role: New role
        email: New email
        license_key: New license key
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        UPDATE users
        SET username = ?,
            password_hash = ?,
            is_admin = ?,
            disabled = ?,
            role = ?,
            email = ?,
            license_key = ?
        WHERE id = ?;
    """
    try:
        curr.execute(sql, (username, password_hash, is_admin, disabled, role, email, license_key, user_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_user(user_id):
    """
    Delete a user by their ID.
    
    Args:
        user_id: The user ID to delete
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("DELETE FROM users WHERE id = ?;", (user_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

