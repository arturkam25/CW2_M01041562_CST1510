import pandas as pd
import random
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
        
        # Fill empty issue_type values during migration
        if 'issue_type' in df.columns:
            mask = df['issue_type'].isna() | (df['issue_type'] == 'None') | (df['issue_type'] == '')
            
            if mask.any():
                common_issue_types = [
                    'Hardware Issue', 'Software Issue', 'Network Problem', 
                    'Account Access', 'Email Problem', 'Printer Issue',
                    'Password Reset', 'System Error', 'Performance Issue', 'Other'
                ]
                
                # Try to infer from description if available
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
                            # Assign random common type
                            df.loc[idx, 'issue_type'] = random.choice(common_issue_types)
                else:
                    # If no description, assign random common types
                    df.loc[mask, 'issue_type'] = [random.choice(common_issue_types) for _ in range(mask.sum())]
        
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
    
    # Fix empty issue_type values - generate based on description or other fields
    if 'issue_type' in df.columns:
        # Replace None, NaN, empty strings with generated values
        mask = df['issue_type'].isna() | (df['issue_type'] == 'None') | (df['issue_type'] == '')
        
        if mask.any():
            # Generate issue types based on description keywords or assign random common types
            common_issue_types = [
                'Hardware Issue', 'Software Issue', 'Network Problem', 
                'Account Access', 'Email Problem', 'Printer Issue',
                'Password Reset', 'System Error', 'Performance Issue', 'Other'
            ]
            
            # Try to infer from description if available
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
                        # Assign random common type
                        import random
                        df.loc[idx, 'issue_type'] = random.choice(common_issue_types)
            else:
                # If no description, assign random common types
                import random
                df.loc[mask, 'issue_type'] = [random.choice(common_issue_types) for _ in range(mask.sum())]
    
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

