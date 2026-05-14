"""
database.py — SQLite helper for TravelMate chatbot
Handles: packages table, learned_responses table
"""

import sqlite3
import os

# Path to the database file (created automatically on first run)
DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")


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

    # Seed packages only if table is empty
    cursor.execute("SELECT COUNT(*) FROM packages")
    if cursor.fetchone()[0] == 0:
        _seed_packages(cursor)

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")


def _seed_packages(cursor):
    """Insert initial holiday package data."""
    packages = [
        (
            "Bali Bliss",
            "Bali, Indonesia",
            "7 nights / 8 days",
            899.00,
            "Enjoy Ubud temples, rice terraces, and Seminyak beaches. Includes hotel & breakfast."
        ),
        (
            "Maldives Dream Escape",
            "Maldives",
            "5 nights / 6 days",
            1499.00,
            "Overwater bungalow, snorkelling, sunset cruises. All-inclusive luxury package."
        ),
        (
            "European Explorer",
            "Paris, Rome, Barcelona",
            "12 nights / 13 days",
            2299.00,
            "Three iconic cities in one trip. Guided tours, 4-star hotels, and airport transfers."
        ),
        (
            "Thailand Adventure",
            "Bangkok & Phuket, Thailand",
            "8 nights / 9 days",
            749.00,
            "Street food tours in Bangkok, island hopping in Phuket. Budget-friendly & action-packed."
        ),
        (
            "Sri Lanka Heritage",
            "Colombo, Kandy & Sigiriya",
            "6 nights / 7 days",
            599.00,
            "Explore ancient ruins, tea plantations, and wildlife safaris. A cultural deep dive."
        ),
        (
            "Dubai Luxury Getaway",
            "Dubai, UAE",
            "4 nights / 5 days",
            1199.00,
            "Burj Khalifa, desert safari, luxury shopping, and fine dining experience included."
        ),
    ]
    cursor.executemany("""
        INSERT INTO packages (name, destination, duration, price_usd, description)
        VALUES (?, ?, ?, ?, ?)
    """, packages)
    print(f"[DB] Seeded {len(packages)} holiday packages.")


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
    like = f"%{keyword}%"
    cursor.execute("""
        SELECT name, destination, duration, price_usd, description
        FROM packages
        WHERE name LIKE ? OR destination LIKE ? OR description LIKE ?
    """, (like, like, like))
    rows = cursor.fetchall()
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
