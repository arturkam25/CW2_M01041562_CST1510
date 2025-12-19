# ==============================================================================
# CYBER INCIDENTS DATA ACCESS LAYER
# ==============================================================================

# This file is responsible for handling all data-related operations
# connected to cyber security incidents within the application.

# Scope of responsibility:
# - migrating cyber incident data from a CSV file into the database
# - reading cyber incident data from the database
# - implementing full CRUD operations (Create, Read, Update, Delete)
#   for the cyber_incidents table

# This file acts as a clear separation layer between:
# - application logic (UI, Streamlit pages, services)
# - and the physical database layer (SQLite)

# Benefits of this approach:
# - application logic does not directly interact with SQL queries
# - the project structure remains clean and modular
# - future extensions (validation, logging, auditing) can be added centrally


import pandas as pd
from .db import get_connection

# ==============================================================================
# DATA MIGRATION
# ==============================================================================

# This section is responsible for controlled data migration
# from a CSV file into the database.

# Typical use cases:
# - first application startup
# - database initialization
# - test data seeding


def migrate_cyber_incidents():
    # Migrates cyber incident records from a CSV file
    # into the cyber_incidents table.
    
    # Process overview:
    # 1. Load DATA/cyber_incidents.csv into a pandas DataFrame
    # 2. Establish a database connection
    # 3. Append data to the cyber_incidents table
    # 4. Close the database connection
    
    # Error handling:
    # - missing CSV file (FileNotFoundError)
    # - any other unexpected exception (database, schema, data issues)
    try:
        df = pd.read_csv("DATA/cyber_incidents.csv")
        conn = get_connection()
        df.to_sql("cyber_incidents", conn, if_exists="append", index=False)
        conn.close()
    except FileNotFoundError:
        print("Warning: cyber_incidents.csv not found")
    except Exception as e:
        print(f"Error migrating cyber incidents: {e}")

# ==============================================================================
# READ OPERATIONS (PANDAS)
# ==============================================================================

# This section provides database read operations
# that return results as pandas DataFrames.

# Particularly useful for:
# - dashboards
# - data visualisation
# - exploratory data analysis (EDA)


def read_all_cyber_incidents():
    # Reads all records from the cyber_incidents table
    # and returns them as a pandas DataFrame.
    
    # Connection safety:
    # - the database connection is always closed using finally
    conn = get_connection()
    try:
        df = pd.read_sql("SELECT * FROM cyber_incidents;", conn)
        return df
    finally:
        conn.close()

# ==============================================================================
# CRUD OPERATIONS
# ==============================================================================

# This section contains classic CRUD operations:
# - Create
# - Read
# - Update
# - Delete

# Design principles:
# - each function opens its own database connection
# - each function performs exactly one responsibility
# - commit is executed only on success
# - rollback is triggered on failure
# - the connection is always closed

# ==============================================================================
# CREATE
# ==============================================================================

def create_incident(incident_id, timestamp, severity, category, status, description):
    # Inserts a new cyber security incident record
    # into the cyber_incidents table.
    
    # Parameters map directly to database columns:
    # - incident_id: unique incident identifier
    # - timestamp: time when the incident occurred
    # - severity: threat level (Low, Medium, High, Critical)
    # - category: incident category
    # - status: current incident state (Open, In Progress, Resolved, Closed)
    # - description: textual incident description
    
    # Transaction safety:
    # - commit on success
    # - rollback and re-raise on error
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

# ==============================================================================
# READ (SINGLE RECORD)
# ==============================================================================

def get_incident_by_id(incident_id):
    # Retrieves a single cyber incident using its unique ID.
    
    # Returns:
    # - a tuple containing the incident record
    # - None if the record does not exist
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            "SELECT * FROM cyber_incidents WHERE incident_id = ?;",
            (incident_id,)
        )
        row = curr.fetchone()
        return row
    finally:
        conn.close()

# ==============================================================================
# READ (ALL RECORDS)
# ==============================================================================

def get_all_incidents():
    # Retrieves all cyber incident records
    # from the cyber_incidents table.
    
    # Returns:
    # - a list of tuples
    
    # Intended for:
    # - backend logic
    # - API responses
    # - lightweight access without pandas
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute("SELECT * FROM cyber_incidents;")
        rows = curr.fetchall()
        return rows
    finally:
        conn.close()

# ==============================================================================
# UPDATE
# ==============================================================================

def update_incident(incident_id, timestamp, severity, category, status, description):
    # Updates an existing cyber incident identified by incident_id.
    
    # All mutable fields are overwritten with new values.
    
    # Transaction rules:
    # - commit only if the update succeeds
    # - rollback on any exception
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
        curr.execute(
            sql,
            (timestamp, severity, category, status, description, incident_id)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

# ==============================================================================
# DELETE
# ==============================================================================

def delete_incident(incident_id):
    # Deletes a cyber incident from the database
    # using its unique incident identifier.
    
    # Notes:
    # - the operation is irreversible
    # - deleting a non-existing record does not raise an SQL error
    conn = get_connection()
    curr = conn.cursor()
    try:
        curr.execute(
            "DELETE FROM cyber_incidents WHERE incident_id = ?;",
            (incident_id,)
        )
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()
