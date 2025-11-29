import pandas as pd
from .db import get_connection


def migrate_tickets():
    """
    Migrate IT tickets from CSV file to database.
    Maps CSV column names to database column names if needed.
    """
    conn = None
    try:
        df = pd.read_csv("DATA/it_tickets.csv")
        conn = get_connection()
        
        # Map CSV column names to database column names if they differ
        column_mapping = {}
        if 'created_at' in df.columns:
            column_mapping['created_at'] = 'created'
        
        # Rename columns if mapping exists
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        # Only select columns that exist in the database table
        db_columns = ['ticket_id', 'created', 'priority', 'issue_type', 'assigned_to', 'status', 'description']
        df = df[[col for col in db_columns if col in df.columns]]
        
        df.to_sql("it_tickets", conn, if_exists="append", index=False)
        conn.close()
    except FileNotFoundError:
        print("Warning: it_tickets.csv not found")
    except Exception as e:
        print(f"Error migrating IT tickets: {e}")
        if conn:
            conn.close()


def read_all_tickets():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM it_tickets;", conn)
    conn.close()
    return df


# CRUD

def create_ticket(ticket_id, created, priority, issue_type, assigned_to, status, description=None):
    """
    Create a new IT ticket.
    
    Args:
        ticket_id: Unique identifier for the ticket
        created: Timestamp when ticket was created
        priority: Priority level (Low, Medium, High, Critical)
        issue_type: Type of issue
        assigned_to: Username of assigned agent
        status: Current status (Open, In Progress, Resolved, Closed)
        description: Optional description of the issue
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO it_tickets
        (ticket_id, created, priority, issue_type, assigned_to, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    curr.execute(sql, (ticket_id, created, priority, issue_type, assigned_to, status, description))
    conn.commit()
    conn.close()


def get_ticket_by_id(ticket_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM it_tickets WHERE ticket_id = ?;", (ticket_id,))
    row = curr.fetchone()
    conn.close()
    return row


def get_all_tickets():
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM it_tickets;")
    rows = curr.fetchall()
    conn.close()
    return rows


def update_ticket(ticket_id, created, priority, issue_type, assigned_to, status, description=None):
    """
    Update an existing IT ticket.
    
    Args:
        ticket_id: Unique identifier for the ticket
        created: Timestamp when ticket was created
        priority: Priority level (Low, Medium, High, Critical)
        issue_type: Type of issue
        assigned_to: Username of assigned agent
        status: Current status (Open, In Progress, Resolved, Closed)
        description: Optional description of the issue
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        UPDATE it_tickets
        SET created = ?,
            priority = ?,
            issue_type = ?,
            assigned_to = ?,
            status = ?,
            description = ?
        WHERE ticket_id = ?;
    """
    curr.execute(sql, (created, priority, issue_type, assigned_to, status, description, ticket_id))
    conn.commit()
    conn.close()


def delete_ticket(ticket_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("DELETE FROM it_tickets WHERE ticket_id = ?;", (ticket_id,))
    conn.commit()
    conn.close()

