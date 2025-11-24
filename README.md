# Week 7 - Secure Authentication System

## Student: Artur Kamerski
## Student ID: M01041562
## Module: CST1510 - BSc Cyber Security and Digital Forensics
## Project: Week 7 Lab - Secure Login & User Authentication
## Coursework Part: Multi-Domain Intelligence Platform - Authentication Module

# 1. Project Overview

This project implements a secure, console based authentication system using Python and the bcrypt hashing library.
It forms the authentication layer of the Multi-Domain Intelligence Platform (CW2) and demonstrates key cybersecurity concepts such as:
- Secure password hashing
- Password strength enforcement
- Lockout after repeated failures
- Account recovery workflows
- Separation of user and admin roles
- Logging and audit trails
- Cross platform secure password input
The system runs on Windows, Linux, and macOS, adjusting password masking behaviour accordingly.

# 2. Key Features

## 2.1 Secure Password Hashing

- Uses bcrypt with automatic salting (bcrypt.gensalt()).
- Plaintext passwords are never stored.
- Password verification uses bcrypt.checkpw().

## 2.2 Cross-Platform Password 

The function input_password():
- Shows * instead of real characters.
- Uses:
    - msvcrt.getch() on Windows,
    - termios + tty on Linux/macOS,
    - falls back to getpass if needed.
Ensures secure password entry on every OS.

## 2.3 Strong Password Policy With Live Feedback

Password must include:
- 8+ characters
- 1 uppercase letter
- 1 lowercase letter
- 1 digit
- 1 special character

During input, requirements are shown with:
- ✔ green checks for satisfied rules
- ✖ blinking red crosses for unmet rules

If all checks pass:
`✔ All password requirements met.`

## 2.4 Username Validation
- 3–20 characters
- Alphanumeric only
- "admin" username automatically becomes an admin role

# 3. Data Storage

## 3.1 Users File - users.txt

Stored in CSV format:
`username,password_hash,failed_attempts,is_locked,role,email,recovery_code`

- failed_attempts - tracks login failures
- is_locked - "1" means account locked
- role - user / admin
- email - always saved in lowercase
- recovery_code - auto generated during registration

Example recovery code:
`ABCD-7X2Q-K91M`

## 3.2 Log File - logs.txt

Every critical event is logged:
`[YYYY-MM-DD HH:MM:SS] Event description...`

Logged events include:
- Registrations
- Logins
- Logouts
- Password resets
- Lockouts
- Admin operations

# 4. Authentication Logic

## 4.1 Login Workflow

login_user_once() implements:
- Username lookup
- Password verification
- Lockout rules
- Resetting failed attempts on success
- After 3 incorrect attempts:

`Your account is LOCKED.`

Admins can later unlock the account.

## 4.2 Lockout Security

- 3 failed logins - account automatically locked
- Lock persists until admin manually unlocks
- User is warned when only 1 attempt remains

## 4.3 Loading Bar Visual Effect

Every major operation displays a loading bar:
`[LOGGING IN] [>>>>>>>>>>>>------] 67%`

Used for:
- Login
- Logout
- Registration
- Password reset
- Account deletion

Adds realism and improves UX.

# 5. User Roles and Menus

## 5.1 User Panel

`--- USER PANEL (username) ---`
`1. Change password`
`2. Delete account`
`3. Logout`

Users can:
- Change their password
- Delete their own account (requires password confirmation)
- Logout with a loading animation

## 5.2 Admin Panel

`--- ADMIN PANEL ---`
`1. List users`
`2. Unlock user`
`3. Reset user password`
`4. Delete user account`
`5. Change my password`
`6. Logout`

Admin capabilities:
- View all users in a formatted table
- Unlock locked accounts
- Reset any user's password
- Delete users (except self deleting)
- Change own password
- Full audit logging

# 6. Account Recovery

## 6.1 Email & Recovery Code

During registration:
- User enters email
- Email is always stored lowercase
- Recovery code is generated and shown
- Used for both username and password recovery
- Enables realistic "Forgot…" flows

## 6.2 Forgot 

User enters:
- Email
- Recovery code

If matched, system displays the username.

## 6.3 Forgot Password

User enters:
- Username
- Email
- Recovery code

Then sets a new password meeting full requirements.

System ensures:
- New password ≠ old password
- Account becomes unlocked
- Failed attempts reset

# 7. Visual UX Features

Loading Bar
Used for login/logout/registration/reset etc.
Colored Output
- Green - success
- Yellow - info
- Red - errors
- Blinking red - password rule not met

# 8. Running the Program

## 8.1 Requirements

`pip install bcrypt`

## 8.2 Start the System

`python auth.py`

Main menu:
`1. Register`
`2. Login`
`3. Exit`

# 9. Files Created

| File       | Purpose                       |
|------------|-------------------------------|
| users.txt  | Stores registered accounts     |
| logs.txt   | Tracks system events           |
| auth.py    | Main authentication module     |

# 10. Limitations and Future Improvements

Current Limitations
- Users stored in plaintext CSV (except passwords).
- No encryption for user file.
- No real email sending.
- No multi factor authentication.

Potential Enhancements
- SQLite database for secure storage
- Email sending for recovery codes
- MFA (SMS/email code)
- Streamlit UI version
- Session tokens for web version
- Encryption of user file

# 11. Summary

This system demonstrates a realistic, multi feature authentication module including:
- Password hashing (bcrypt)
- Full password policy enforcement
- Login lockout security
- Recovery mechanisms
- Role based control
- User and admin panels
- Logging and auditing
- Cross platform password masking
- Visual loading effects

It forms a strong security foundation for the Multi-Domain Intelligence Platform (CW2).
