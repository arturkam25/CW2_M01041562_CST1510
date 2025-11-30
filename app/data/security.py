import re
import bcrypt
import random
import string


def validate_password_strength(password):
    checks = {
        "min_length": len(password) >= 8,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digit": bool(re.search(r"[0-9]", password)),
        "special": bool(re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",.<>/?\\|`~]", password))
    }
    return all(checks.values()), checks


def password_feedback(checks):
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
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_recovery_code():
    """Generate a recovery code in format XXXX-XXXX-XXXX"""
    parts = []
    for _ in range(3):
        part = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        parts.append(part)
    return "-".join(parts)


def is_valid_email(email):
    """Validate email format"""
    if not email or len(email) > 254 or " " in email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def authenticate_user(username, password):
    """
    Authenticate a user by username and password.
    
    Args:
        username: Username to authenticate
        password: Plain text password
        
    Returns:
        tuple: (success: bool, user_data: dict or None, message: str)
        If successful, returns (True, user_dict, "Login successful")
        If failed, returns (False, None, error_message)
    """
    # Import here to avoid circular import
    try:
        from .users import get_user_by_username
    except ImportError:
        # Fallback if relative import fails
        from app.data.users import get_user_by_username
    
    user = get_user_by_username(username)
    
    if not user:
        return False, None, "Invalid username or password."
    
    # user tuple structure: (id, username, password_hash, is_admin, disabled, role, email, license_key)
    user_id, db_username, password_hash, is_admin, disabled, role, email, license_key = user[:8]
    
    # Check if user is disabled
    if disabled:
        return False, None, "This account is disabled."
    
    # Verify password
    if not verify_password(password, password_hash):
        return False, None, "Invalid username or password."
    
    # Return user data as dictionary
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

