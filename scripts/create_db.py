# scripts/create_db.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interview_system.api.database import create_all_tables
from interview_system.models import user # Ensure all models are imported

def main():
    print("Creating all database tables...")
    create_all_tables()
    print("Tables created successfully.")

if __name__ == "__main__":
    main()