from .db import get_connection
import random
import string


# ============================================================
# LICENSE KEY GENERATOR – 12 znaków w formacie XXXX-XXXX-XXXX
# ============================================================
def generate_license_key():
    """Generate a 12-character license key in XXXX-XXXX-XXXX format."""
    def block():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{block()}-{block()}-{block()}"


def create_tables():
    """
    Create all database tables if they don't exist.
    This function should be called before any data operations.
    """
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
            license_key TEXT
        );
    """)
    
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


