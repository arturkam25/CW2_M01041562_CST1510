import pandas as pd

from .db import get_connection

def migrate_datasets():
    df = pd.read_csv("DATA/datasets_metadata.csv")
    conn = get_connection()
    df.to_sql("datasets_metadata", conn, if_exists="append", index=False)
    conn.close()

def read_all_datasets():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM datasets_metadata;", conn)
    conn.close()
    return df

# CRUD

def create_dataset(dataset_id, name, rows, columns, uploaded_by=None, upload_date=None):
    """
    Create a new dataset metadata record.
    
    Args:
        dataset_id: Unique identifier for the dataset
        name: Name of the dataset
        rows: Number of rows in the dataset
        columns: Number of columns in the dataset
        uploaded_by: Username who uploaded the dataset (optional)
        upload_date: Date when dataset was uploaded (optional)
    """
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

def get_dataset_by_id(dataset_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM datasets_metadata WHERE dataset_id = ?;", (dataset_id,))
    row = curr.fetchone()
    conn.close()
    return row

def get_all_datasets():
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM datasets_metadata;")
    rows = curr.fetchall()
    conn.close()
    return rows

def update_dataset(dataset_id, name, rows, columns, uploaded_by=None, upload_date=None):
    """
    Update an existing dataset metadata record.
    
    Args:
        dataset_id: Unique identifier for the dataset
        name: Name of the dataset
        rows: Number of rows in the dataset
        columns: Number of columns in the dataset
        uploaded_by: Username who uploaded the dataset (optional)
        upload_date: Date when dataset was uploaded (optional)
    """
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

def delete_dataset(dataset_id):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("DELETE FROM datasets_metadata WHERE dataset_id = ?;", (dataset_id,))
    conn.commit()
    conn.close()

