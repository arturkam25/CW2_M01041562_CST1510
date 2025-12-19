# ==============================================================================
# USER SERVICE INITIALISATION AND MIGRATION
# ==============================================================================

# This file provides high-level service functions
# related to user data initialisation and migration.

# Scope of responsibility:
# - migrating users from external files into the database
# - initialising predefined test users
# - acting as a thin service layer above the users data module

# Architectural role:
# - service layer module
# - orchestrates user-related setup operations
# - separates application bootstrap logic from data access logic

from app.data.users import load_users_from_file, add_test_users

# ==============================================================================
# USER DATA MIGRATION
# ==============================================================================

# This section contains functions responsible for
# importing user data into the database.

def migrate_users():
    # Migrates users from an external file into the database.
    #
    # This function delegates the actual loading logic
    # to the users data access layer.
    
    # Typical use cases:
    # - first application startup
    # - database initialisation
    # - environment reset
    load_users_from_file()

# ==============================================================================
# TEST USER INITIALISATION
# ==============================================================================

# This section provides helper functions for
# inserting predefined test users.

def initialize_test_users():
    # Inserts predefined test users into the database.
    
    # Intended for:
    # - development environments
    # - testing and demonstrations
    # - non-production setups
    add_test_users()
