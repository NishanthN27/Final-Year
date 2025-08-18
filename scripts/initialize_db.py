import os
import sys

# This line adds the project's root directory to Python's path.
# It allows the script to find and import modules from your 'interview_system' package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interview_system.api.database import create_all_tables
from interview_system.models.user import User  # <-- IMPORTANT

def main():
    """
    Main function to create database tables.
    """
    print("Connecting to the database and creating tables...")
    
    # This function uses the engine configured in database.py 
    # and creates all tables that inherit from the Base class.
    # The 'User' model must be imported for SQLAlchemy to find it.
    create_all_tables()
    
    print("Tables created successfully!")

if __name__ == "__main__":
    main()