from .db import get_connection
from .schema import generate_license_key
# Import security functions inside functions to avoid circular import


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
        # Ensure columns exist before selecting
        try:
            curr.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;")
            conn.commit()
        except:
            pass
        try:
            curr.execute("ALTER TABLE users ADD COLUMN recovery_code TEXT;")
            conn.commit()
        except:
            pass
        
        curr.execute("SELECT * FROM users WHERE username = ?;", (username,))
        row = curr.fetchone()
        if row:
            failed_att = row[8] if len(row) > 8 else None
            disabled_val = row[4] if len(row) > 4 else None
            print(f"DEBUG get_user_by_username: Found user {username}, row length: {len(row)}, failed_attempts: {failed_att}, disabled: {disabled_val}")
            print(f"DEBUG get_user_by_username: Full row: {row}")
        else:
            print(f"DEBUG get_user_by_username: User {username} not found!")
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
        # Import here to avoid circular import
        from .security import validate_password_strength, password_feedback, hash_password
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
# ACCOUNT SECURITY FUNCTIONS
# ===============================

def update_user_failed_attempts(user_id, failed_attempts):
    """Update failed login attempts for a user. Like in terminal code: user["failed_attempts"] = value"""
    conn = get_connection()
    curr = conn.cursor()
    try:
        # Ensure column exists
        try:
            curr.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;")
            conn.commit()
        except Exception as e:
            print(f"DEBUG update_user_failed_attempts: Column might exist: {e}")
        
        # Update failed attempts (like in terminal code: save_users(users))
        curr.execute("UPDATE users SET failed_attempts = ? WHERE id = ?", (int(failed_attempts), user_id))
        conn.commit()
        
        # Verify update
        curr.execute("SELECT failed_attempts FROM users WHERE id = ?", (user_id,))
        result = curr.fetchone()
        if result:
            print(f"DEBUG update_user_failed_attempts: Updated user {user_id} to {failed_attempts}, DB now has: {result[0]}")
        else:
            print(f"DEBUG update_user_failed_attempts: WARNING - User {user_id} not found after update!")
    except Exception as e:
        conn.rollback()
        print(f"ERROR update_user_failed_attempts: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()


def lock_user_account(user_id):
    """Lock a user account by setting disabled flag. Like in terminal code: user["is_locked"] = "1" """
    conn = get_connection()
    curr = conn.cursor()
    try:
        # Ensure columns exist
        try:
            curr.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;")
            conn.commit()
        except:
            pass
        
        # Lock account (like in terminal code: user["is_locked"] = "1", user["failed_attempts"] = 3)
        curr.execute("UPDATE users SET disabled = 1, failed_attempts = 3 WHERE id = ?", (user_id,))
        conn.commit()
        print(f"DEBUG: Locked account for user {user_id}")
    except Exception as e:
        conn.rollback()
        print(f"Error locking account: {e}")
    finally:
        conn.close()


def unlock_user_account(user_id):
    """Unlock a user account and reset failed attempts."""
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("UPDATE users SET disabled = 0, failed_attempts = 0 WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User unlocked successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()


def get_user_by_email(email):
    """Get a user by their email address."""
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = curr.fetchone()
        return row
    finally:
        conn.close()


def generate_recovery_code_for_user(user_id):
    """Generate and save a recovery code for a user."""
    # Import here to avoid circular import
    from .security import generate_recovery_code
    recovery_code = generate_recovery_code()
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("UPDATE users SET recovery_code = ? WHERE id = ?", (recovery_code, user_id))
        conn.commit()
        return recovery_code
    except Exception as e:
        conn.rollback()
        return None
    finally:
        conn.close()


def reset_password_with_recovery(username, email, recovery_code, new_password):
    """
    Reset password using recovery code or license key.
    
    Args:
        username: Username
        email: User email
        recovery_code: Recovery code or license key
        new_password: New password
        
    Returns:
        tuple: (success: bool, message: str)
    """
    from .security import validate_password_strength, password_feedback, hash_password
    
    # Validate password
    valid, checks = validate_password_strength(new_password)
    if not valid:
        return False, password_feedback(checks)
    
    user = get_user_by_username(username)
    if not user:
        return False, "User not found."
    
    # Handle old and new schema
    if len(user) >= 10:
        user_id, db_username, password_hash, is_admin, disabled, role, db_email, license_key, failed_attempts, db_recovery_code = user
    else:
        user_id, db_username, password_hash, is_admin, disabled, role, db_email, license_key = user
        db_recovery_code = None
    
    # Verify email
    if db_email.lower() != email.lower():
        return False, "Email does not match."
    
    # Verify recovery code or license key
    recovery_code_upper = recovery_code.upper().strip()
    license_key_upper = license_key.upper().strip() if license_key else ""
    db_recovery_code_upper = db_recovery_code.upper().strip() if db_recovery_code else ""
    
    if recovery_code_upper != db_recovery_code_upper and recovery_code_upper != license_key_upper:
        return False, "Invalid recovery code or license key."
    
    # Check if new password is same as old
    from .security import verify_password
    if verify_password(new_password, password_hash):
        return False, "New password cannot be the same as the old password."
    
    # Update password and reset failed attempts
    new_password_hash = hash_password(new_password)
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("""
            UPDATE users SET 
                password_hash = ?,
                failed_attempts = 0,
                disabled = 0
            WHERE id = ?
        """, (new_password_hash, user_id))
        conn.commit()
        return True, "Password reset successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()


def get_user_by_username_for_recovery(username):
    """Get user data including recovery code for password recovery."""
    user = get_user_by_username(username)
    if not user:
        return None
    
    # Handle old and new schema
    if len(user) >= 10:
        user_id, db_username, password_hash, is_admin, disabled, role, email, license_key, failed_attempts, recovery_code = user
    else:
        user_id, db_username, password_hash, is_admin, disabled, role, email, license_key = user
        failed_attempts = 0
        recovery_code = None
    
    return {
        "id": user_id,
        "username": db_username,
        "email": email,
        "license_key": license_key,
        "recovery_code": recovery_code,
        "failed_attempts": failed_attempts or 0,
        "disabled": bool(disabled)
    }


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
    # Import here to avoid circular import
    from .security import is_valid_email, generate_recovery_code, validate_password_strength, password_feedback, hash_password
    
    # Validate email
    if email and not is_valid_email(email):
        return False, "Invalid email format."
    
    # 1. validate password strength
    valid, checks = validate_password_strength(password)
    if not valid:
        return False, password_feedback(checks)
    
    # 2. hash password
    password_hash = hash_password(password)
    
    license_key = generate_license_key()
    recovery_code = generate_recovery_code()
    
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO users
        (username, password_hash, is_admin, disabled, role, email, license_key, failed_attempts, recovery_code)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?)
    """
    try:
        curr.execute(sql, (
            username,
            password_hash,
            _bool(is_admin),
            _bool(disabled),
            role,
            email.lower() if email else "",
            license_key,
            recovery_code
        ))
        conn.commit()
        return True, f"User '{username}' created successfully.\nLicense Key: {license_key}\nRecovery Code: {recovery_code}"
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()


