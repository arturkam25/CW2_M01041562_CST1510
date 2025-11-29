import sqlite3

DB_PATH = "DATA/inteligence_platform.db"


def get_connection():
    return sqlite3.connect(DB_PATH)

