# scripts/create_db.py
import sys
import pathlib

# Add the project's src directory to the path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Now we can import from our application
from interview_system.api.database import create_all_tables
from interview_system.models import user # This import is needed for the table to be recognized

def main():
    print("Creating all database tables...")
    create_all_tables()
    print("Done.")

if __name__ == "__main__":
    main()