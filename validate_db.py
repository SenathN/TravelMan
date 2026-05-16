
import os
import sys
from database import initialise_db, get_all_packages, DB_PATH

def validate():
    print(f"Checking database at: {DB_PATH}")
    
    # 1. Initialize/Seed
    try:
        initialise_db()
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        return False

    # 2. Check if file exists
    if not os.path.exists(DB_PATH):
        print(f"ERROR: Database file {DB_PATH} was not created.")
        return False

    # 3. Check data
    try:
        packages = get_all_packages()
        count = len(packages)
        print(f"Success: Found {count} packages in database.")
        if count == 0:
            print("ERROR: Database is empty after seeding.")
            return False
        return True
    except Exception as e:
        print(f"ERROR: Failed to query database: {e}")
        return False

if __name__ == "__main__":
    if validate():
        print("Validation PASSED.")
        sys.exit(0)
    else:
        print("Validation FAILED.")
        sys.exit(1)
