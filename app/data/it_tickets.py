# ==============================================================================
# IT TICKETS DATA ACCESS LAYER
# ==============================================================================

# This file is responsible for handling all data-related operations
# connected to IT support tickets within the application.

# Scope of responsibility:
# - migrating IT ticket data from a CSV file into the database
# - normalising and completing ticket metadata during migration
# - reading IT ticket data from the database
# - implementing full CRUD operations (Create, Read, Update, Delete)
#   for the it_tickets table

# This file acts as a separation layer between:
# - application logic (UI, dashboards, services)
# - and the physical database layer (SQLite)

# Benefits of this approach:
# - complex data-cleaning logic is isolated from the UI
# - database access remains consistent and reusable
# - ticket data integrity is improved at ingestion time

import pandas as pd
import random
from .db import get_connection

# ==============================================================================
# DATA MIGRATION
# ==============================================================================

# This section is responsible for controlled migration
# of IT ticket data from a CSV file into the database.

# During migration:
# - column names are mapped to database schema
# - missing or invalid issue_type values are inferred or generated
# - only valid database columns are inserted

def migrate_tickets():
    # Migrates IT ticket records from a CSV file
    # into the it_tickets table.

    # Process overview:
    # 1. Load DATA/it_tickets.csv into a pandas DataFrame
    # 2. Map CSV column names to database column names if required
    # 3. Filter columns to match the database schema
    # 4. Fill missing issue_type values using heuristics or random selection
    # 5. Append records to the it_tickets table

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
        db_columns = [
            'ticket_id',
            'created',
            'priority',
            'issue_type',
            'assigned_to',
            'status',
            'description'
        ]
        df = df[[col for col in db_columns if col in df.columns]]
        # Fill empty issue_type values during migration
        if 'issue_type' in df.columns:
            mask = df['issue_type'].isna() | (df['issue_type'] == 'None') | (df['issue_type'] == '')

            if mask.any():
                common_issue_types = [
                    'Hardware Issue',
                    'Software Issue',
                    'Network Problem',
                    'Account Access',
                    'Email Problem',
                    'Printer Issue',
                    'Password Reset',
                    'System Error',
                    'Performance Issue',
                    'Other'
                ]
                # Try to infer issue type from description if available
                if 'description' in df.columns:
                    for idx in df[mask].index:
                        desc = str(df.loc[idx, 'description']).lower()
                        if any(word in desc for word in ['password', 'login', 'access']):
                            df.loc[idx, 'issue_type'] = 'Account Access'
                        elif any(word in desc for word in ['printer', 'print']):
                            df.loc[idx, 'issue_type'] = 'Printer Issue'
                        elif any(word in desc for word in ['email', 'mail']):
                            df.loc[idx, 'issue_type'] = 'Email Problem'
                        elif any(word in desc for word in ['network', 'internet', 'connection']):
                            df.loc[idx, 'issue_type'] = 'Network Problem'
                        elif any(word in desc for word in ['hardware', 'computer', 'laptop']):
                            df.loc[idx, 'issue_type'] = 'Hardware Issue'
                        elif any(word in desc for word in ['software', 'application', 'program']):
                            df.loc[idx, 'issue_type'] = 'Software Issue'
                        else:
                            df.loc[idx, 'issue_type'] = random.choice(common_issue_types)
                else:
                    df.loc[mask, 'issue_type'] = [
                        random.choice(common_issue_types) for _ in range(mask.sum())
                    ]

        df.to_sql("it_tickets", conn, if_exists="append", index=False)
        conn.close()
    except FileNotFoundError:
        print("Warning: it_tickets.csv not found")
    except Exception as e:
        print(f"Error migrating IT tickets: {e}")
        if conn:
            conn.close()

# ==============================================================================
# READ OPERATIONS (PANDAS)
# ==============================================================================

# This section provides read operations that return
# IT ticket data as pandas DataFrames.

# Additional normalisation is applied after reading:
# - missing issue_type values are generated if required

def read_all_tickets():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM it_tickets;", conn)
    conn.close()
    # Fix empty issue_type values after reading from the database
    if 'issue_type' in df.columns:
        mask = df['issue_type'].isna() | (df['issue_type'] == 'None') | (df['issue_type'] == '')

        if mask.any():
            common_issue_types = [
                'Hardware Issue',
                'Software Issue',
                'Network Problem',
                'Account Access',
                'Email Problem',
                'Printer Issue',
                'Password Reset',
                'System Error',
                'Performance Issue',
                'Other'
            ]

            if 'description' in df.columns:
                for idx in df[mask].index:
                    desc = str(df.loc[idx, 'description']).lower()
                    if any(word in desc for word in ['password', 'login', 'access']):
                        df.loc[idx, 'issue_type'] = 'Account Access'
                    elif any(word in desc for word in ['printer', 'print']):
                        df.loc[idx, 'issue_type'] = 'Printer Issue'
                    elif any(word in desc for word in ['email', 'mail']):
                        df.loc[idx, 'issue_type'] = 'Email Problem'
                    elif any(word in desc for word in ['network', 'internet', 'connection']):
                        df.loc[idx, 'issue_type'] = 'Network Problem'
                    elif any(word in desc for word in ['hardware', 'computer', 'laptop']):
                        df.loc[idx, 'issue_type'] = 'Hardware Issue'
                    elif any(word in desc for word in ['software', 'application', 'program']):
                        df.loc[idx, 'issue_type'] = 'Software Issue'
                    else:
                        df.loc[idx, 'issue_type'] = random.choice(common_issue_types)
            else:
                df.loc[mask, 'issue_type'] = [
                    random.choice(common_issue_types) for _ in range(mask.sum())
                ]

    return df

# ==============================================================================
# CRUD OPERATIONS
# ==============================================================================

# This section implements classic CRUD operations:
# - Create
# - Read
# - Update
# - Delete

# ==============================================================================
# CREATE
# ==============================================================================

def create_ticket(ticket_id, created, priority, issue_type, assigned_to, status, description=None):
    # Inserts a new IT support ticket
    # into the it_tickets table.
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO it_tickets
        (ticket_id, created, priority, issue_type, assigned_to, status, description)
        VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    curr.execute(
        sql,
        (ticket_id, created, priority, issue_type, assigned_to, status, description)
    )
    conn.commit()
    conn.close()

# ==============================================================================
# READ (SINGLE RECORD)
# ==============================================================================

def get_ticket_by_id(ticket_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM it_tickets WHERE ticket_id = ?;", (ticket_id,))
    row = curr.fetchone()
    conn.close()
    return row

# ==============================================================================
# READ (ALL RECORDS)
# ==============================================================================

def get_all_tickets():
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM it_tickets;")
    rows = curr.fetchall()
    conn.close()
    return rows

# ==============================================================================
# UPDATE
# ==============================================================================

def update_ticket(ticket_id, created, priority, issue_type, assigned_to, status, description=None):
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
    curr.execute(
        sql,
        (created, priority, issue_type, assigned_to, status, description, ticket_id)
    )
    conn.commit()
    conn.close()

# ==============================================================================
# DELETE
# ==============================================================================

def delete_ticket(ticket_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("DELETE FROM it_tickets WHERE ticket_id = ?;", (ticket_id,))
    conn.commit()
    conn.close()
