# ==============================================================================
# AUTHENTICATION, PASSWORD SECURITY AND RECOVERY UTILITIES
# ==============================================================================

# This file provides all security-related helper functions
# used by the authentication and user management layers
# of the application.

# Scope of responsibility:
# - validating password strength against security rules
# - providing user-friendly feedback for weak passwords
# - hashing passwords using bcrypt
# - verifying passwords during authentication
# - generating account recovery codes
# - validating email address format
# - authenticating users with account lockout protection

# Architectural role:
# - shared security utility module
# - independent from UI and database layers
# - imported by authentication, registration and admin workflows

# Security considerations:
# - no plaintext passwords are ever stored
# - password verification uses secure hashing
# - repeated failed login attempts result in account lockout

import re
import bcrypt
import random
import string

# ==============================================================================
# PASSWORD VALIDATION AND HASHING
# ==============================================================================

# This section contains all logic related to password
# strength validation, feedback generation and secure hashing.

def validate_password_strength(password):
    # Validates a password against a predefined set
    # of security requirements.
    
    # Validation rules enforced:
    # - minimum length
    # - at least one uppercase letter
    # - at least one lowercase letter
    # - at least one digit
    # - at least one special character
    
    # Returns:
    # - boolean indicating overall validity
    # - dictionary containing results for each rule
    checks = {
        "min_length": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"[0-9]", password)),
        "special": bool(
            re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",.<>/?\\|`~]", password)
        )
    }
    return all(checks.values()), checks

def password_feedback(checks):
    # Generates human-readable feedback messages
    # based on which password validation rules failed.
    
    # Intended use:
    # - user registration forms
    # - password change workflows
    # - administrative user creation
    messages = []
    if not checks["min_length"]:
        messages.append("Password must have at least 8 characters.")
    if not checks["uppercase"]:
        messages.append("Password must include an uppercase letter.")
    if not checks["lowercase"]:
        messages.append("Password must include a lowercase letter.")
    if not checks["digit"]:
        messages.append("Password must include a digit.")
    if not checks["special"]:
        messages.append("Password must include a special character.")
    return messages


def hash_password(password):
    # Hashes a plaintext password using bcrypt.
    
    # Security notes:
    # - bcrypt automatically handles salting
    # - the returned hash is safe to store in the database
    # - plaintext passwords are never persisted
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

def verify_password(password, hashed):
    # Verifies a plaintext password against a stored bcrypt hash.
    
    # Returns:
    # - True if the password matches the hash
    # - False otherwise
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

# ==============================================================================
# RECOVERY AND EMAIL VALIDATION
# ==============================================================================

# This section contains helper functions related to
# account recovery and email validation.

def generate_recovery_code():
    # Generates a recovery code in the format XXXX-XXXX-XXXX.
    
    # Intended use:
    # - account recovery
    # - password reset workflows
    # - administrative user assistance
    parts = []
    for _ in range(3):
        part = "".join(
            random.choice(string.ascii_uppercase + string.digits)
            for _ in range(4)
        )
        parts.append(part)
    return "-".join(parts)


def is_valid_email(email):
    # Validates an email address using basic constraints
    # and a standard regular expression.
    
    # Validation rules:
    # - must not be empty
    # - must not exceed 254 characters
    # - must not contain whitespace
    # - must match common email format
    if not email or len(email) > 254 or " " in email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

# ==============================================================================
# AUTHENTICATION WITH ACCOUNT LOCKOUT
# ==============================================================================

# This section implements user authentication logic
# with protection against brute-force attacks.

def authenticate_user(username, password):
    # Authenticates a user using username and password.
    
    # Security features:
    # - failed login attempts are counted
    # - account is locked after a fixed number of failures
    # - supports backward compatibility with older database schemas
    try:
        from .users import (
            get_user_by_username,
            update_user_failed_attempts,
            lock_user_account
        )
    except ImportError:
        from app.data.users import (
            get_user_by_username,
            update_user_failed_attempts,
            lock_user_account
        )

    MAX_ATTEMPTS = 3

    user = get_user_by_username(username)

    if not user:
        return False, None, "Invalid username or password."
    # Handle old and new database schema safely
    if len(user) >= 9:
        (
            user_id,
            db_username,
            password_hash,
            is_admin,
            disabled,
            role,
            email,
            license_key,
            failed_attempts
        ) = user[:9]
    else:
        (
            user_id,
            db_username,
            password_hash,
            is_admin,
            disabled,
            role,
            email,
            license_key
        ) = user[:8]
        failed_attempts = 0
    # Account already locked
    if disabled:
        return False, None, (
            "Your account has been locked after multiple failed login attempts. "
            "Please contact the administrator."
        )
    # Correct password
    if verify_password(password, password_hash):
        update_user_failed_attempts(user_id, 0)

        user_data = {
            "id": user_id,
            "username": db_username,
            "is_admin": bool(is_admin),
            "disabled": bool(disabled),
            "role": role,
            "email": email,
            "license_key": license_key
        }

        return True, user_data, "Login successful."
    # Incorrect password
    failed_attempts = (failed_attempts or 0) + 1
    update_user_failed_attempts(user_id, failed_attempts)

    remaining = MAX_ATTEMPTS - failed_attempts

    if remaining <= 0:
        lock_user_account(user_id)
        return False, None, (
            "Your account has been locked after 3 failed login attempts. "
            "Please contact the administrator."
        )

    return False, None, (
        f"Invalid password. {remaining} attempt(s) remaining "
        "before your account is locked."
    )
