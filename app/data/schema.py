# ==============================================================================
# DATABASE SCHEMA AND LICENSE KEY UTILITIES
# ==============================================================================

# This file is responsible for defining the database schema
# and providing utility functions required at database level.

# Scope of responsibility:
# - generating license keys for users
# - creating database tables if they do not exist
# - performing safe schema upgrades for existing databases

# Architectural role:
# - infrastructure-level module
# - executed during application initialisation
# - ensures database consistency before any data operations

from .db import get_connection
import random
import string

# ==============================================================================
# LICENSE KEY GENERATOR
# ==============================================================================

# This section provides a utility function for generating
# license keys in a fixed, human-readable format.

def generate_license_key():
    # Generates a 12-character license key
    # in the format XXXX-XXXX-XXXX.
    def block():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{block()}-{block()}-{block()}"

# ==============================================================================
# DATABASE SCHEMA CREATION
# ==============================================================================

# This section is responsible for creating all required
# database tables if they do not already exist.

# It also performs safe schema updates for existing databases
# by adding missing columns when required.

def create_tables():
    # Creates all database tables required by the application.
    
    # This function must be executed before any read or write
    # operations are performed on the database.
    conn = get_connection()
    curr = conn.cursor()
    # Users table
    curr.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER,
            disabled INTEGER,
            role TEXT,
            email TEXT,
            license_key TEXT,
            failed_attempts INTEGER DEFAULT 0,
            recovery_code TEXT
        );
    """)
    # Add missing columns for existing databases
    try:
        curr.execute("SELECT failed_attempts FROM users LIMIT 1;")
    except:
        try:
            curr.execute(
                "ALTER TABLE users ADD COLUMN failed_attempts INTEGER DEFAULT 0;"
            )
            conn.commit()
        except:
            pass

    try:
        curr.execute("SELECT recovery_code FROM users LIMIT 1;")
    except:
        try:
            curr.execute(
                "ALTER TABLE users ADD COLUMN recovery_code TEXT;"
            )
            conn.commit()
        except:
            pass
    # Cyber incidents table
    curr.execute("""
        CREATE TABLE IF NOT EXISTS cyber_incidents (
            incident_id INTEGER,
            timestamp TEXT,
            severity TEXT,
            category TEXT,
            status TEXT,
            description TEXT
        );
    """)
    # Datasets metadata table
    curr.execute("""
        CREATE TABLE IF NOT EXISTS datasets_metadata (
            dataset_id INTEGER,
            name TEXT,
            rows INTEGER,
            columns INTEGER,
            uploaded_by TEXT,
            upload_date TEXT
        );
    """)
    # IT tickets table
    curr.execute("""
        CREATE TABLE IF NOT EXISTS it_tickets (
            ticket_id INTEGER,
            created TEXT,
            priority TEXT,
            issue_type TEXT,
            assigned_to TEXT,
            status TEXT,
            description TEXT
        );
    """)

    conn.commit()
    conn.close()
