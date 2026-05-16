"""
database.py — SQLite helper for TravelMate chatbot
Handles: packages table, learned_responses table
"""

import sqlite3
import os
import sys
import json

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_db_path():
    """
    Get the path to the database file in a private application directory.
    Ensures the database is not in a publicly accessible location.
    """
    app_name = "TravelMate"
    if sys.platform == "win32":
        # Windows: %LOCALAPPDATA%\TravelMate\chatbot.db
        base_dir = os.environ.get("LOCALAPPDATA", os.path.expanduser("~\\AppData\\Local"))
    elif sys.platform == "darwin":
        # macOS: ~/Library/Application Support/TravelMate/chatbot.db
        base_dir = os.path.expanduser("~/Library/Application Support")
    else:
        # Linux/Other: ~/.local/share/TravelMate/chatbot.db
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    
    app_dir = os.path.join(base_dir, app_name)
    
    # Ensure the directory exists
    try:
        if not os.path.exists(app_dir):
            os.makedirs(app_dir, exist_ok=True)
    except Exception as e:
        # Fallback to current directory if app data is not writable
        print(f"[DB] Warning: Could not create private directory {app_dir}: {e}")
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(app_dir, "chatbot.db")

# Path to the database file (created automatically on first run)
DB_PATH = get_db_path()


def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def initialise_db():
    """
    Create tables if they don't exist and seed initial package data.
    Called once at bot startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Table 1: Holiday Packages ---
    # Stores live travel packages (can be updated by admin)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            destination TEXT NOT NULL,
            duration    TEXT NOT NULL,
            price_usd   REAL NOT NULL,
            description TEXT
        )
    """)

    # --- Table 2: Learned Responses ---
    # Bot stores answers it learns from users (machine learning tier)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learned_responses (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL UNIQUE,
            answer   TEXT NOT NULL
        )
    """)

    # Always re-seed packages to ensure latest metadata is available (Requirement 2)
    _seed_packages(cursor)

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")


def _seed_packages(cursor):
    """Insert initial holiday package data from packages.json."""
    # Clear existing packages to avoid duplicates when re-seeding
    cursor.execute("DELETE FROM packages")
    
    packages_file = get_resource_path('packages.json')
    if not os.path.exists(packages_file):
        print(f"[DB] Warning: {packages_file} not found. Skipping seeding.")
        return

    try:
        with open(packages_file, 'r', encoding='utf-8') as f:
            packages_data = json.load(f)
        
        packages = [
            (p['name'], p['destination'], p['duration'], p['price_usd'], p['description'])
            for p in packages_data
        ]
        
        cursor.executemany("""
            INSERT INTO packages (name, destination, duration, price_usd, description)
            VALUES (?, ?, ?, ?, ?)
        """, packages)
        print(f"[DB] Seeded {len(packages)} holiday packages from metadata.")
    except Exception as e:
        print(f"[DB] Error seeding packages: {e}")


# ─── Query Functions ──────────────────────────────────────────────

def get_all_packages():
    """Return all packages as a list of dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, destination, duration, price_usd, description FROM packages")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"name": r[0], "destination": r[1], "duration": r[2], "price": r[3], "description": r[4]}
        for r in rows
    ]


def search_packages(keyword):
    """Search packages by keyword in name, destination, or description."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try exact-ish match first
    like = f"%{keyword}%"
    cursor.execute("""
        SELECT name, destination, duration, price_usd, description
        FROM packages
        WHERE name LIKE ? OR destination LIKE ? OR description LIKE ?
    """, (like, like, like))
    rows = cursor.fetchall()
    
    # If no results, try a broader search or let the engine handle fuzzy
    conn.close()
    return [
        {"name": r[0], "destination": r[1], "duration": r[2], "price": r[3], "description": r[4]}
        for r in rows
    ]


def save_learned_response(question, answer):
    """Save a new Q&A pair learned from the user."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO learned_responses (question, answer)
            VALUES (?, ?)
        """, (question.lower().strip(), answer.strip()))
        conn.commit()
        print(f"[DB] Learned: '{question}' → '{answer}'")
    except Exception as e:
        print(f"[DB] Error saving learned response: {e}")
    finally:
        conn.close()


def get_learned_response(question):
    """Look up a previously learned answer for a given question."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT answer FROM learned_responses
        WHERE question = ?
    """, (question.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# ─── Quick test ───────────────────────────────────────────────────
if __name__ == "__main__":
    initialise_db()
    print("\nAll packages:")
    for p in get_all_packages():
        print(f"  {p['name']} | {p['destination']} | {p['duration']} | ${p['price']}")
    print("\nSearch 'bali':")
    for p in search_packages("bali"):
        print(f"  {p['name']} — {p['description']}")
