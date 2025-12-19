# ==============================================================================
# DATABASE CONNECTION CONFIGURATION
# ==============================================================================

# This file is responsible for defining and providing
# a single, centralised database connection mechanism
# for the entire application.

# Scope of responsibility:
# - defining the database file location
# - exposing a reusable connection factory function

# Architectural role:
# - acts as the lowest-level infrastructure module
# - used by all data access layers (DAL)
# - ensures consistent database access across the project

import sqlite3

DB_PATH = "DATA/inteligence_platform.db"

def get_connection():
    # Creates and returns a new SQLite database connection.
    
    # Design notes:
    # - a new connection is created per call
    # - connection lifecycle is managed by the caller
    # - this approach avoids shared-state issues
    return sqlite3.connect(DB_PATH)
