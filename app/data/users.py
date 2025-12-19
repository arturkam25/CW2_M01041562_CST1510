# ==============================================================================
# USERS DATA ACCESS AND SECURITY OPERATIONS
# ==============================================================================

# This file is responsible for all database-level operations
# related to user accounts within the application.

# Scope of responsibility:
# - creating and loading users
# - full CRUD operations for users
# - handling authentication-related account state
# - managing failed login attempts and account lockout
# - supporting password recovery workflows
# - ensuring backward compatibility with older database schemas

# Architectural role:
# - data access layer (DAL) for users
# - bridge between authentication logic and the database
# - central place for user-related persistence logic

# Security considerations:
# - password hashes are stored, never plaintext passwords
# - failed login attempts are tracked persistently
# - account lockout is enforced at database level
# - recovery codes and license keys are handled securely

from .db import get_connection
from .schema import generate_license_key

# ==============================================================================
# INTERNAL HELPERS
# ==============================================================================

# This section contains small internal helper functions
# used to normalise input values before database operations.

def _bool(value):
    # Converts None or string "None" to integer 0.
    # Ensures consistent boolean storage in the database.
    return 0 if value in (None, "None") else int(value)

# ==============================================================================
# USER CREATION AND INITIAL LOADING
# ==============================================================================

# This section contains functions used to create users
# and populate the database from external sources.

def add_user_full(username, password_hash, is_admin, disabled, role, email, license_key):
    # Adds a user to the database using INSERT OR IGNORE.
    
    # This approach prevents duplicate users from being created
    # when loading data multiple times.
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT OR IGNORE INTO users 
        (username, password_hash, is_admin, disabled, role, email, license_key)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        curr.execute(
            sql,
            (username, password_hash, is_admin, disabled, role, email, license_key)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def load_users_from_file(path="DATA/users.txt"):
    # Loads users from a text file and inserts them into the database.
    
    # Expected file format:
    # username,password_hash,is_admin,disabled,role,email,license_key
    try:
        with open(path, "r") as f:
            lines = f.readlines()

        for line in lines:
            parts = line.strip().split(',')
            if len(parts) != 7:
                continue

            (
                username,
                password_hash,
                is_admin,
                disabled,
                role,
                email,
                license_key
            ) = parts

            add_user_full(
                username,
                password_hash,
                is_admin,
                disabled,
                role,
                email,
                license_key
            )
    except FileNotFoundError:
        print(f"Warning: Users file not found at {path}")
    except Exception as e:
        print(f"Error loading users from file: {e}")

def add_test_users():
    # Adds simple test users to the database.
    #
    # Intended only for development and testing.
    add_user_full("alice", "hashed_password_123", None, None, None, None, None)
    add_user_full("bob", "hashed_password_456", None, None, None, None, None)

# ==============================================================================
# CRUD OPERATIONS
# ==============================================================================

# This section implements standard CRUD operations
# for user accounts.

def create_user(username, password_hash, is_admin, disabled, role, email, license_key):
    # Creates a new user record and returns its database ID.
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO users
        (username, password_hash, is_admin, disabled, role, email, license_key)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    try:
        curr.execute(
            sql,
            (username, password_hash, is_admin, disabled, role, email, license_key)
        )
        conn.commit()
        return curr.lastrowid
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_user_by_id(user_id):
    # Retrieves a user record by its unique ID.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        return curr.fetchone()
    finally:
        conn.close()

def get_user_by_username(username):
    # Retrieves a user record by username.
    
    # This function also ensures that required columns
    # exist for backward compatibility with older databases.
    conn = get_connection()
    curr = conn.cursor()
    try:
        try:
            curr.execute(
                "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;"
            )
            conn.commit()
        except:
            pass

        try:
            curr.execute(
                "ALTER TABLE users ADD COLUMN recovery_code TEXT;"
            )
            conn.commit()
        except:
            pass

        curr.execute("SELECT * FROM users WHERE username = ?;", (username,))
        row = curr.fetchone()

        if row:
            print(
                f"DEBUG get_user_by_username: Found user {username}, "
                f"row length: {len(row)}"
            )
        else:
            print(f"DEBUG get_user_by_username: User {username} not found")

        return row
    finally:
        conn.close()

def get_all_users():
    # Retrieves all users from the database.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users ORDER BY is_admin DESC, id ASC")
        return curr.fetchall()
    finally:
        conn.close()

def update_user(user_id, username, password=None, is_admin=0, disabled=0, role="user", email="", license_key=None):
    # Updates an existing user record.
    
    # If a new password is provided, it is validated and hashed.
    conn = get_connection()
    curr = conn.cursor()

    if password:
        from .security import validate_password_strength, password_feedback, hash_password
        valid, checks = validate_password_strength(password)
        if not valid:
            conn.close()
            return False, password_feedback(checks)
        password_hash = hash_password(password)
    else:
        curr.execute(
            "SELECT password_hash FROM users WHERE id = ?",
            (user_id,)
        )
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
        curr.execute(
            sql,
            (
                username,
                password_hash,
                _bool(is_admin),
                _bool(disabled),
                role,
                email,
                license_key,
                user_id
            )
        )
        conn.commit()
        return True, "User updated."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()

def delete_user(user_id):
    # Deletes a user record by ID.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return True, "User deleted."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()

# ==============================================================================
# ACCOUNT SECURITY OPERATIONS
# ==============================================================================

# This section contains functions responsible for
# account lockout, failed login tracking and recovery.

def update_user_failed_attempts(user_id, failed_attempts):
    # Updates the number of failed login attempts for a user.
    conn = get_connection()
    curr = conn.cursor()
    try:
        try:
            curr.execute(
                "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;"
            )
            conn.commit()
        except:
            pass

        curr.execute(
            "UPDATE users SET failed_attempts = ? WHERE id = ?",
            (int(failed_attempts), user_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"ERROR update_user_failed_attempts: {e}")
    finally:
        conn.close()

def lock_user_account(user_id):
    # Locks a user account after repeated failed login attempts.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            "UPDATE users SET disabled = 1, failed_attempts = 3 WHERE id = ?",
            (user_id,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error locking account: {e}")
    finally:
        conn.close()

def unlock_user_account(user_id):
    # Unlocks a user account and resets failed login attempts.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            "UPDATE users SET disabled = 0, failed_attempts = 0 WHERE id = ?",
            (user_id,)
        )
        conn.commit()
        return True, "User unlocked successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()

def get_user_by_email(email):
    # Retrieves a user record by email address.
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        return curr.fetchone()
    finally:
        conn.close()

def generate_recovery_code_for_user(user_id):
    # Generates and stores a recovery code for a user.
    from .security import generate_recovery_code
    recovery_code = generate_recovery_code()
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            "UPDATE users SET recovery_code = ? WHERE id = ?",
            (recovery_code, user_id)
        )
        conn.commit()
        return recovery_code
    except Exception:
        conn.rollback()
        return None
    finally:
        conn.close()

def reset_password_with_recovery(username, email, recovery_code, new_password):
    # Resets a user's password using a recovery code or license key.
    from .security import validate_password_strength, password_feedback, hash_password, verify_password

    valid, checks = validate_password_strength(new_password)
    if not valid:
        return False, password_feedback(checks)

    user = get_user_by_username(username)
    if not user:
        return False, "User not found."

    if len(user) >= 10:
        (
            user_id,
            _,
            password_hash,
            _,
            _,
            _,
            db_email,
            license_key,
            _,
            db_recovery_code
        ) = user
    else:
        (
            user_id,
            _,
            password_hash,
            _,
            _,
            _,
            db_email,
            license_key
        ) = user
        db_recovery_code = None

    if db_email.lower() != email.lower():
        return False, "Email does not match."

    recovery_code_upper = recovery_code.upper().strip()
    license_key_upper = license_key.upper().strip() if license_key else ""
    db_recovery_code_upper = db_recovery_code.upper().strip() if db_recovery_code else ""

    if (
        recovery_code_upper != db_recovery_code_upper
        and recovery_code_upper != license_key_upper
    ):
        return False, "Invalid recovery code or license key."

    if verify_password(new_password, password_hash):
        return False, "New password cannot be the same as the old password."

    new_password_hash = hash_password(new_password)
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            """
            UPDATE users SET
                password_hash = ?,
                failed_attempts = 0,
                disabled = 0
            WHERE id = ?
            """,
            (new_password_hash, user_id)
        )
        conn.commit()
        return True, "Password reset successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()

# ==============================================================================
# SECURE USER REGISTRATION
# ==============================================================================

# This section provides high-level user creation
# with full validation and security handling.

def create_user_secure(username, password, is_admin, disabled, role, email):
    # Creates a new user with full validation,
    # hashing and recovery code generation.
    from .security import (
        is_valid_email,
        generate_recovery_code,
        validate_password_strength,
        password_feedback,
        hash_password
    )

    if email and not is_valid_email(email):
        return False, "Invalid email format."

    valid, checks = validate_password_strength(password)
    if not valid:
        return False, password_feedback(checks)

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
        curr.execute(
            sql,
            (
                username,
                password_hash,
                _bool(is_admin),
                _bool(disabled),
                role,
                email.lower() if email else "",
                license_key,
                recovery_code
            )
        )
        conn.commit()
        return True, (
            f"User '{username}' created successfully.\n"
            f"License Key: {license_key}\n"
            f"Recovery Code: {recovery_code}"
        )
    except Exception as e:
        conn.rollback()
        return False, f"Database error: {e}"
    finally:
        conn.close()

def register_user_public(username, password, email):
    # Public-facing user registration function.
    
    # Rules:
    # - always non-admin
    # - always enabled
    # - role is fixed to "user"
    success, message = create_user_secure(
        username=username,
        password=password,
        is_admin=0,
        disabled=0,
        role="user",
        email=email
    )

    if not success:
        return False, message

    license_line = None
    for line in message.splitlines():
        if "License Key:" in line:
            license_line = line.strip()
            break

    if not license_line:
        return False, "Account created, but license key could not be retrieved."

    return True, license_line
