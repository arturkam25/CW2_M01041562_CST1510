import bcrypt
import os
import re
import time
import sys
from datetime import datetime
import random
import string
import csv

# Cross-platform password input support
try:
    import msvcrt  # Windows
    WINDOWS = True
except ImportError:
    try:
        import termios
        import tty
        WINDOWS = False
    except ImportError:
        WINDOWS = None

USER_DATA_FILE = "users.txt"
LOG_FILE = "logs.txt"

# -----------------------------------
# COLORS
# -----------------------------------
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BLINK = "\033[5m"

# -----------------------------------
# LOGGING
# -----------------------------------
def write_log(message):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"{RED}Warning: Could not write to log file: {e}{RESET}")

# -----------------------------------
# LOADING BAR
# -----------------------------------
def loading_bar(text="[PROCESSING]", duration=1.6):
    length = 20
    start = time.time()
    while True:
        elapsed = time.time() - start
        progress = elapsed / duration
        if progress > 1:
            progress = 1
        filled = int(length * progress)
        empty = length - filled
        bar = ">" * filled + "-" * empty
        percent = int(progress * 100)
        sys.stdout.write(f"\r{YELLOW}{text}{RESET} {GREEN}[{bar}]{RESET} {percent}%")
        sys.stdout.flush()
        if progress >= 1:
            break
        time.sleep(0.08)
    print()

# -----------------------------------
# PASSWORD INPUT
# -----------------------------------
def input_password(prompt="Password: "):
    print(prompt, end="", flush=True)
    password = ""

    if WINDOWS is True:
        while True:
            ch = msvcrt.getch()
            if ch in {b"\r", b"\n"}:
                print()
                return password
            if ch == b"\x08":
                if len(password) > 0:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)
                continue
            if ch in {b"\x00", b"\xe0"}:
                msvcrt.getch()
                continue
            try:
                password += ch.decode("utf-8")
            except:
                continue
            print("*", end="", flush=True)

    elif WINDOWS is False:
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    ch = sys.stdin.read(1)
                    if ch in ("\r", "\n"):
                        print()
                        break
                    elif ch in ("\x7f", "\b"):
                        if len(password) > 0:
                            password = password[:-1]
                            print("\b \b", end="", flush=True)
                    elif ch == "\x03":
                        raise KeyboardInterrupt
                    else:
                        password += ch
                        print("*", end="", flush=True)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            import getpass
            return getpass.getpass(prompt)

    else:
        import getpass
        return getpass.getpass(prompt)

    return password

# -----------------------------------
# PASSWORD REQUIREMENTS
# -----------------------------------
def print_password_requirements_colored(password):
    checks = {
        "At least 8 characters long": len(password) >= 8,
        "At least one uppercase letter (A-Z)": bool(re.search(r"[A-Z]", password)),
        "At least one lowercase letter (a-z)": bool(re.search(r"[a-z]", password)),
        "At least one digit (0-9)": bool(re.search(r"[0-9]", password)),
        "At least one special character": bool(
            re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",.<>/?\\|`~]", password)
        ),
    }
    all_ok = all(checks.values())
    if all_ok:
        print(f"{GREEN}✔ All password requirements met.{RESET}")
        return True

    print(f"{YELLOW}\nPassword requirements:{RESET}")
    for text, ok in checks.items():
        if ok:
            print(f"{GREEN}✔ {text}{RESET}")
        else:
            print(f"{BLINK}{RED}✖ {text}{RESET}")
    return False

# -----------------------------------
# RECOVERY CODE GENERATOR
# -----------------------------------
def generate_recovery_code():
    parts = []
    for _ in range(3):
        part = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(4))
        parts.append(part)
    return "-".join(parts)

# -----------------------------------
# LOAD / SAVE USERS
# -----------------------------------
def load_users():
    users = []
    if not os.path.exists(USER_DATA_FILE):
        return users
    try:
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) < 2:
                    continue

                username = row[0]
                password_hash = row[1]
                failed_attempts = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
                is_locked = row[3] if len(row) > 3 and row[3] in ("0", "1") else "0"
                role = row[4] if len(row) > 4 else "user"
                email = row[5] if len(row) > 5 else ""
                recovery_code = row[6] if len(row) > 6 else ""

                users.append({
                    "username": username,
                    "password_hash": password_hash,
                    "failed_attempts": failed_attempts,
                    "is_locked": is_locked,
                    "role": role,
                    "email": email.lower(),
                    "recovery_code": recovery_code,
                })
    except Exception as e:
        print(f"{RED}Error loading users: {e}{RESET}")
        write_log(f"Error loading users: {e}")
    return users

def save_users(users):
    try:
        with open(USER_DATA_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            for u in users:
                writer.writerow([
                    u.get("username", ""),
                    u.get("password_hash", ""),
                    u.get("failed_attempts", 0),
                    u.get("is_locked", "0"),
                    u.get("role", "user"),
                    u.get("email", ""),
                    u.get("recovery_code", ""),
                ])
    except Exception as e:
        print(f"{RED}Error saving users: {e}{RESET}")
        write_log(f"Error saving users: {e}")

def find_user(users, username):
    for u in users:
        if u["username"] == username:
            return u
    return None

# -----------------------------------
# PASSWORD HASH
# -----------------------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except:
        return False

# -----------------------------------
# EMAIL VALIDATION
# -----------------------------------
def is_valid_email(email):
    if not email or len(email) > 254 or " " in email:
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

# -----------------------------------
# REGISTER USER
# -----------------------------------
def register_user(username, password, email):
    users = load_users()
    if find_user(users, username):
        print(f"{RED}Error: Username '{username}' already exists.{RESET}")
        return False

    role = "admin" if username.lower() == "admin" else "user"
    recovery_code = generate_recovery_code()

    user = {
        "username": username,
        "password_hash": hash_password(password),
        "failed_attempts": 0,
        "is_locked": "0",
        "role": role,
        "email": email.lower(),
        "recovery_code": recovery_code,
    }

    users.append(user)
    save_users(users)

    write_log(f"User '{username}' registered (role={role})")
    print(f"{GREEN}Success: User '{username}' registered!{RESET}")
    print(f"{YELLOW}Your recovery code (please make a note): {recovery_code}{RESET}")
    return True

# -----------------------------------
# LOGIN FLOW
# -----------------------------------
def login_user_once(username, password):
    users = load_users()
    user = find_user(users, username)

    if not user:
        return False, "no_user"

    if user["is_locked"] == "1":
        return False, "locked"

    if verify_password(password, user["password_hash"]):
        user["failed_attempts"] = 0
        user["is_locked"] = "0"
        save_users(users)
        return True, "ok"

    user["failed_attempts"] += 1
    if user["failed_attempts"] >= 3:
        user["is_locked"] = "1"
        save_users(users)
        return False, "locked"

    save_users(users)
    return False, "wrong_password"

# -----------------------------------
# DELETE OWN ACCOUNT
# -----------------------------------
def delete_user_self(username):
    users = load_users()
    user = find_user(users, username)

    if not user:
        print(f"{RED}User not found.{RESET}")
        return False

    pw = input_password("Enter your password to confirm deletion: ")
    if not verify_password(pw, user["password_hash"]):
        print(f"{RED}Incorrect password.{RESET}")
        return False

    loading_bar("[DELETING ACCOUNT]")
    write_log(f"User '{username}' deleted themselves")

    users = [u for u in users if u["username"] != username]
    save_users(users)

    print(f"{GREEN}Your account has been deleted.{RESET}")
    return True

# -----------------------------------
# CHANGE PASSWORD
# -----------------------------------
def change_password(username):
    users = load_users()
    user = find_user(users, username)

    current = input_password("Enter current password: ")
    if not verify_password(current, user["password_hash"]):
        print(f"{RED}Error: Incorrect current password.{RESET}")
        return False

    print(f"""
{YELLOW}Password requirements:{RESET}
• 8+ chars
• Uppercase
• Lowercase
• Digit
• Special character
""")

    while True:
        new = input_password("New password: ")

        if new == current:
            print(f"{RED}New password cannot be same as old.{RESET}")
            continue

        if not print_password_requirements_colored(new):
            continue

        confirm = input_password("Confirm password: ")
        if new != confirm:
            print(f"{RED}Passwords do not match.{RESET}")
            continue
        break

    loading_bar("[UPDATING PASSWORD]")

    user["password_hash"] = hash_password(new)
    user["failed_attempts"] = 0
    user["is_locked"] = "0"
    save_users(users)

    print(f"{GREEN}Password updated successfully.{RESET}")
    write_log(f"User '{username}' changed password")
    return True

# -----------------------------------
# FORGOT USERNAME
# -----------------------------------
def forgot_username_flow():
    print("\n--- FORGOT USERNAME ---")
    email = input("Email: ").strip().lower()
    recovery = input("Recovery code: ").strip().upper()

    users = load_users()
    for u in users:
        if u["email"].lower() == email.lower() and u["recovery_code"].upper() == recovery:
            print(f"{GREEN}Your username is: {u['username']}{RESET}")
            write_log(f"Username recovery for email '{email}'")
            return

    print(f"{RED}No match found.{RESET}")

# -----------------------------------
# FORGOT PASSWORD
# -----------------------------------
def forgot_password_flow(username_from_login=None):
    print("\n--- FORGOT PASSWORD ---")

    if username_from_login:
        username = username_from_login
        print(f"Resetting password for: {username}")
    else:
        username = input("Username: ").strip()

    email = input("Email: ").strip().lower()
    recovery = input("Recovery code: ").strip().upper()

    users = load_users()
    user = find_user(users, username)

    if not user:
        print(f"{RED}User not found.{RESET}")
        return

    if user["email"].lower() != email.lower() or user["recovery_code"].upper() != recovery:
        print(f"{RED}Invalid email or recovery code.{RESET}")
        return

    print(f"""
{YELLOW}Password requirements:{RESET}
• 8+ chars
• Uppercase
• Lowercase
• Digit
• Special character
""")

    while True:
        new_password = input_password("New password: ")

        if verify_password(new_password, user["password_hash"]):
            print(f"{RED}New password cannot be same as old.{RESET}")
            continue

        if not print_password_requirements_colored(new_password):
            continue

        confirm = input_password("Confirm password: ")
        if new_password != confirm:
            print(f"{RED}Passwords do not match.{RESET}")
            continue
        break

    loading_bar("[RESETTING PASSWORD]")

    user["password_hash"] = hash_password(new_password)
    user["failed_attempts"] = 0
    user["is_locked"] = "0"
    save_users(users)

    write_log(f"User '{username}' reset password via recovery")
    print(f"{GREEN}Password reset successfully.{RESET}")

# -----------------------------------
# ADMIN FUNCTIONS
# -----------------------------------
def admin_list_users():
    users = load_users()
    print("\nCurrent users:")
    print("---------------------------------------------------------------------")
    print(f"{'Username':<16}{'Role':<12}{'Locked':<12}{'Attempts':<10}{'Email':<25}")
    print("---------------------------------------------------------------------")
    for u in users:
        locked = "YES" if u["is_locked"] == "1" else "NO"
        print(f"{u['username']:<16}{u['role']:<12}{locked:<12}{str(u['failed_attempts']):<10}{u['email']:<25}")
    print("---------------------------------------------------------------------")

def admin_unlock_user():
    users = load_users()
    target = input("Username to unlock: ").strip()
    user = find_user(users, target)

    if not user:
        print(f"{RED}User not found.{RESET}")
        return

    loading_bar("[UNLOCKING USER]")
    user["failed_attempts"] = 0
    user["is_locked"] = "0"
    save_users(users)

    write_log(f"Admin unlocked '{target}'")
    print(f"{GREEN}User unlocked.{RESET}")

def admin_reset_password(admin_username):
    users = load_users()

    print("\n--- ADMIN PASSWORD RESET ---")
    confirm_admin = input_password("Enter your admin password to continue: ")

    admin_user = find_user(users, admin_username)
    if not verify_password(confirm_admin, admin_user["password_hash"]):
        print(f"{RED}Admin authentication failed.{RESET}")
        return

    target = input("Reset password for user: ").strip()
    user = find_user(users, target)

    if not user:
        print(f"{RED}User not found.{RESET}")
        return

    print(f"""
{YELLOW}New password must meet requirements:{RESET}
• 8+ chars
• Uppercase
• Lowercase
• Digit
• Special char
""")

    while True:
        pw = input_password("New password: ")
        if not print_password_requirements_colored(pw):
            continue
        confirm = input_password("Confirm password: ")
        if pw != confirm:
            print(f"{RED}Passwords do not match.{RESET}")
            continue
        break

    loading_bar("[RESETTING PASSWORD]")

    user["password_hash"] = hash_password(pw)
    user["failed_attempts"] = 0
    user["is_locked"] = "0"
    save_users(users)

    write_log(f"Admin reset password for '{target}'")
    print(f"{GREEN}Password reset successful.{RESET}")

def admin_delete_user(admin_username):
    users = load_users()
    target = input("Delete user: ").strip()

    if target == admin_username:
        print(f"{RED}Admin cannot delete themselves.{RESET}")
        return

    user = find_user(users, target)
    if not user:
        print(f"{RED}User not found.{RESET}")
        return

    confirm = input(f"Are you sure (y/N)? ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    loading_bar("[DELETING USER]")

    users = [u for u in users if u["username"] != target]
    save_users(users)

    write_log(f"Admin deleted '{target}'")
    print(f"{GREEN}User deleted.{RESET}")

# -----------------------------------
# PANELS
# -----------------------------------
def user_panel(username):
    while True:
        print(f"""
--- USER PANEL ({username}) ---
1. Change password
2. Delete account
3. Logout
""")
        choice = input("Select (1-3): ").strip()

        if choice == "1":
            change_password(username)
        elif choice == "2":
            if delete_user_self(username):
                break
        elif choice == "3":
            loading_bar("[LOGGING OUT]")
            print(f"{GREEN}Logout successful.{RESET}")
            write_log(f"User '{username}' logged out")
            break
        else:
            print(f"{RED}Invalid option.{RESET}")

def admin_panel(username):
    while True:
        print(f"""
--- ADMIN PANEL ---
1. List users
2. Unlock user
3. Reset user password
4. Delete user account
5. Change my password
6. Logout
""")
        choice = input("Select (1-6): ").strip()

        if choice == "1":
            admin_list_users()
        elif choice == "2":
            admin_unlock_user()
        elif choice == "3":
            admin_reset_password(username)
        elif choice == "4":
            admin_delete_user(username)
        elif choice == "5":
            change_password(username)
        elif choice == "6":
            loading_bar("[LOGGING OUT]")
            print(f"{GREEN}Admin logged out.{RESET}")
            write_log(f"Admin '{username}' logged out")
            break
        else:
            print(f"{RED}Invalid option.{RESET}")

# -----------------------------------
# VALIDATION
# -----------------------------------
def validate_username(username):
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be 3-20 characters."
    if not username.isalnum():
        return False, "Username must be alphanumeric."
    return True, ""

# -----------------------------------
# MAIN MENU
# -----------------------------------
def display_menu():
    print("  MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print("  Secure Authentication System")
    print("\n1. Register")
    print("2. Login")
    print("3. Exit")

# -----------------------------------
# MAIN PROGRAM
# -----------------------------------
def main():
    print("\nWelcome to the Week 7 Authentication System!")
    while True:
        display_menu()
        choice = input("Select (1-3): ").strip()

        # REGISTER
        if choice == "1":
            print("\n--- REGISTER ---")
            username = input("Username: ").strip()
            ok, msg = validate_username(username)
            if not ok:
                print(f"{RED}{msg}{RESET}")
                continue

            while True:
                email = input("Email: ").strip().lower()
                if not is_valid_email(email):
                    print(f"{RED}Invalid email.{RESET}")
                    continue
                break

            print(f"""
{YELLOW}Password requirements:{RESET}
• 8+ chars
• Uppercase
• Lowercase
• Digit
• Special char
""")

            while True:
                pw = input_password("Password: ")
                if not print_password_requirements_colored(pw):
                    continue
                confirm = input_password("Confirm: ")
                if pw != confirm:
                    print(f"{RED}Passwords do not match.{RESET}")
                    continue
                break

            loading_bar("[REGISTERING USER]")
            register_user(username, pw, email)

        # LOGIN
        elif choice == "2":
            print("\n--- LOGIN ---")
            username = input("Username: ").strip()

            users = load_users()
            user = find_user(users, username)

            if not user:
                print(f"{RED}User not found.{RESET}")
                forgot = input(f"{YELLOW}Forgot username? (y/N): {RESET}").strip().lower()
                if forgot == "y":
                    forgot_username_flow()
                continue

            first_password_attempt = True

            while True:
                pw = input_password("Password: ")
                ok, status = login_user_once(username, pw)

                if ok:
                    loading_bar("[LOGGING IN]")
                    print(f"{GREEN}Welcome {username}!{RESET}")
                    write_log(f"User '{username}' logged in")

                    if user["role"] == "admin":
                        admin_panel(username)
                    else:
                        user_panel(username)
                    break

                if status == "wrong_password":
                    attempts = user["failed_attempts"]
                    left = 3 - attempts

                    print(f"{RED}Wrong password.{RESET}")
                    print(f"{YELLOW}Attempts left: {left}{RESET}")
                    if left == 1:
                        print(f"{RED}One more attempt will lock your account!{RESET}")

                    if first_password_attempt:
                        print("\n1. Try again")
                        print("2. Forgot password?")
                        action = input("Select (1-2): ").strip()
                        if action == "2":
                            forgot_password_flow(username)
                            break
                        first_password_attempt = False

                    continue

                if status == "locked":
                    print(f"{RED}Your account is LOCKED.{RESET}")
                    write_log(f"User '{username}' locked themselves out")
                    break

        # EXIT
        elif choice == "3":
            loading_bar("[EXITING]")
            print("Goodbye!")
            break

        else:
            print(f"{RED}Invalid option.{RESET}")

# -----------------------------------
# ENTRY POINT
# -----------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Interrupted by user.{RESET}")
    except Exception as e:
        print(f"\n{RED}Unexpected error: {e}{RESET}")
        write_log(f"Unexpected error: {e}")