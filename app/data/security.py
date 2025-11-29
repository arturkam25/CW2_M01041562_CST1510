import re
import bcrypt


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
    from .users import get_user_by_username
    
    user = get_user_by_username(username)
    
    if not user:
        return False, None, "Invalid username or password."
    
    # user tuple structure: (id, username, password_hash, is_admin, disabled, role, email, license_key)
    user_id, db_username, password_hash, is_admin, disabled, role, email, license_key = user
    
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

