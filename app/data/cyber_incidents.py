import pandas as pd
from .db import get_connection


def migrate_cyber_incidents():
    """
    Migrate cyber incidents from CSV file to database.
    """
    try:
        df = pd.read_csv("DATA/cyber_incidents.csv")
        conn = get_connection()
        df.to_sql("cyber_incidents", conn, if_exists="append", index=False)
        conn.close()
    except FileNotFoundError:
        print("Warning: cyber_incidents.csv not found")
    except Exception as e:
        print(f"Error migrating cyber incidents: {e}")


def read_all_cyber_incidents():
    """
    Read all cyber incidents from the database.
    
    Returns:
        pandas.DataFrame: DataFrame containing all cyber incidents
    """
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM cyber_incidents;", conn)
        return df
    finally:
        conn.close()


# CRUD

def create_incident(incident_id, timestamp, severity, category, status, description):
    """
    Create a new cyber incident.
    
    Args:
        incident_id: Unique identifier for the incident
        timestamp: Timestamp when incident occurred
        severity: Severity level (Low, Medium, High, Critical)
        category: Incident category
        status: Current status (Open, In Progress, Resolved, Closed)
        description: Description of the incident
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO cyber_incidents
        (incident_id, timestamp, severity, category, status, description)
        VALUES (?, ?, ?, ?, ?, ?);
    """
    try:
        curr.execute(sql, (incident_id, timestamp, severity, category, status, description))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_incident_by_id(incident_id):
    """
    Get a cyber incident by its ID.
    
    Args:
        incident_id: The incident ID
        
    Returns:
        tuple: Incident record or None if not found
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM cyber_incidents WHERE incident_id = ?;", (incident_id,))
        row = curr.fetchone()
        return row
    finally:
        conn.close()


def get_all_incidents():
    """
    Get all cyber incidents from the database.
    
    Returns:
        list: List of all incident records
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM cyber_incidents;")
        rows = curr.fetchall()
        return rows
    finally:
        conn.close()


def update_incident(incident_id, timestamp, severity, category, status, description):
    """
    Update an existing cyber incident.
    
    Args:
        incident_id: The incident ID to update
        timestamp: New timestamp
        severity: New severity level
        category: New category
        status: New status
        description: New description
    """
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        UPDATE cyber_incidents
        SET timestamp = ?,
            severity = ?,
            category = ?,
            status = ?,
            description = ?
        WHERE incident_id = ?;
    """
    try:
        curr.execute(sql, (timestamp, severity, category, status, description, incident_id))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_incident(incident_id):
    """
    Delete a cyber incident by its ID.
    
    Args:
        incident_id: The incident ID to delete
    """
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("DELETE FROM cyber_incidents WHERE incident_id = ?;", (incident_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

