# ==============================================================================
# DATASETS METADATA DATA ACCESS LAYER
# ==============================================================================

# This file is responsible for handling all data-related operations
# connected to dataset metadata within the application.

# Scope of responsibility:
# - migrating dataset metadata from a CSV file into the database
# - reading dataset metadata from the database
# - implementing full CRUD operations (Create, Read, Update, Delete)
#   for the datasets_metadata table

# This file acts as a separation layer between:
# - application logic (UI, Streamlit pages, services)
# - and the physical database layer (SQLite)

# Benefits of this approach:
# - SQL logic is isolated from the application layer
# - metadata handling remains consistent and reusable
# - future extensions (validation, access control, auditing) can be added centrally

import pandas as pd
from .db import get_connection

# ==============================================================================
# DATA MIGRATION
# ==============================================================================

# This section is responsible for controlled migration
# of dataset metadata from a CSV file into the database.

# Typical use cases:
# - initial database population
# - environment setup
# - test data seeding

def migrate_datasets():
    # Migrates dataset metadata records from a CSV file
    # into the datasets_metadata table.

    # Process overview:
    # 1. Load DATA/datasets_metadata.csv into a pandas DataFrame
    # 2. Establish a database connection
    # 3. Append records to the datasets_metadata table
    # 4. Close the database connection
    df = pd.read_csv("DATA/datasets_metadata.csv")
    conn = get_connection()
    df.to_sql("datasets_metadata", conn, if_exists="append", index=False)
    conn.close()

# ==============================================================================
# READ OPERATIONS (PANDAS)
# ==============================================================================

# This section provides read operations that return
# dataset metadata as pandas DataFrames.

# Particularly useful for:
# - dataset listings
# - dashboards
# - administrative views

def read_all_datasets():
    # Reads all records from the datasets_metadata table
    # and returns them as a pandas DataFrame.
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM datasets_metadata;", conn)
    conn.close()
    return df

# ==============================================================================
# CRUD OPERATIONS
# ==============================================================================

# This section implements classic CRUD operations:
# - Create
# - Read
# - Update
# - Delete

# Design principles:
# - each function manages its own database connection
# - each function has a single, well-defined responsibility
# - database state is committed explicitly
# - connections are always closed after use

# ==============================================================================
# CREATE
# ==============================================================================

def create_dataset(dataset_id, name, rows, columns, uploaded_by=None, upload_date=None):
    # Inserts a new dataset metadata record
    # into the datasets_metadata table.

    # Parameters map directly to database columns:
    # - dataset_id: unique dataset identifier
    # - name: dataset name
    # - rows: number of rows in the dataset
    # - columns: number of columns in the dataset
    # - uploaded_by: user who uploaded the dataset (optional)
    # - upload_date: upload timestamp or date (optional)
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        INSERT INTO datasets_metadata
        (dataset_id, name, rows, columns, uploaded_by, upload_date)
        VALUES (?, ?, ?, ?, ?, ?);
    """
    curr.execute(sql, (dataset_id, name, rows, columns, uploaded_by, upload_date))
    conn.commit()
    conn.close()

# ==============================================================================
# READ (SINGLE RECORD)
# ==============================================================================

def get_dataset_by_id(dataset_id):
    # Retrieves a single dataset metadata record
    # using its unique dataset identifier.

    # Returns:
    # - a tuple representing the dataset metadata
    # - None if the record does not exist
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM datasets_metadata WHERE dataset_id = ?;", (dataset_id,))
    row = curr.fetchone()
    conn.close()
    return row

# ==============================================================================
# READ (ALL RECORDS)
# ==============================================================================

def get_all_datasets():
    # Retrieves all dataset metadata records
    # from the datasets_metadata table.

    # Returns:
    # - a list of tuples

    # Intended for:
    # - backend logic
    # - API responses
    # - lightweight access without pandas
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM datasets_metadata;")
    rows = curr.fetchall()
    conn.close()
    return rows

# ==============================================================================
# UPDATE
# ==============================================================================

def update_dataset(dataset_id, name, rows, columns, uploaded_by=None, upload_date=None):
    # Updates an existing dataset metadata record
    # identified by dataset_id.

    # All mutable fields are overwritten with new values.
    conn = get_connection()
    curr = conn.cursor()
    sql = """
        UPDATE datasets_metadata
        SET name = ?,
            rows = ?,
            columns = ?,
            uploaded_by = ?,
            upload_date = ?
        WHERE dataset_id = ?;
    """
    curr.execute(sql, (name, rows, columns, uploaded_by, upload_date, dataset_id))
    conn.commit()
    conn.close()

# ==============================================================================
# DELETE
# ==============================================================================

def delete_dataset(dataset_id):
    # Deletes a dataset metadata record
    # from the database using its unique identifier.

    # Notes:
    # - the operation is irreversible
    # - deleting a non-existing record does not raise an SQL error
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?;", (dataset_id,))
    conn.commit()
    conn.close()
