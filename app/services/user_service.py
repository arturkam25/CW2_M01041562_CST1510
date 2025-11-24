"""
User service module for migration and user-related operations.
"""
from app.data.users import load_users_from_file, add_test_users


def migrate_users():
    """
    Migrate users from file to database.
    This function loads users from the users.txt file.
    """
    load_users_from_file()


def initialize_test_users():
    """
    Initialize test users in the database.
    """
    add_test_users()

