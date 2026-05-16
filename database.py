"""
database.py — SQLite helper for TravelMate chatbot
Handles: packages table, learned_responses table
"""

import sqlite3
import os
import sys
import shutil

def get_data_path(filename):
    """ Get path to persistent data in user's home directory """
    if sys.platform == "win32":
        # Windows: %APPDATA%/TravelMate
        app_data = os.environ.get("APPDATA")
        if not app_data:
            app_data = os.path.expanduser("~")
        base_path = os.path.join(app_data, "TravelMate")
    else:
        # Linux/macOS: ~/.travelmate
        base_path = os.path.expanduser("~/.travelmate")
    
    try:
        if not os.path.exists(base_path):
            os.makedirs(base_path)
    except Exception:
        # Fallback to current directory if home is not writable
        base_path = "."
        
    return os.path.join(base_path, filename)

def _get_seed_db_path():
    """Return the bundled clean seed DB path if available."""
    meipass = getattr(sys, '_MEIPASS', None)
    candidates = []
    if meipass:
        candidates.extend([
            os.path.join(meipass, 'data', 'seed_chatbot.db'),
            os.path.join(meipass, 'seed_chatbot.db')
        ])
    candidates.append(os.path.join(os.path.dirname(__file__), 'data', 'seed_chatbot.db'))

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return None


def _user_db_needs_seed(path):
    """Return True if the user DB is missing or contains no package rows."""
    if not os.path.exists(path):
        return True
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='packages'")
        if not cursor.fetchone():
            return True
        cursor.execute("SELECT COUNT(*) FROM packages")
        count = cursor.fetchone()[0]
        return count == 0
    except Exception:
        return True
    finally:
        try:
            conn.close()
        except Exception:
            pass

# Path to the user database file (the running app stores learned responses here)
USER_DB_PATH = get_data_path("chatbot.db")
DB_PATH = USER_DB_PATH

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)

def initialise_db():
    """
    Create tables if they don't exist and seed initial package data.
    Called once at bot startup.
    """
    print(f"[DB] Initialising database at {DB_PATH}...")
    
    # 1. Check if we need to seed from a bundled DB file
    seeded_db_src = _get_seed_db_path()
    if seeded_db_src and _user_db_needs_seed(DB_PATH):
        try:
            print(f"[DB] Seeding from bundled database: {seeded_db_src}")
            shutil.copyfile(seeded_db_src, DB_PATH)
            print(f"[DB] Successfully seeded from {os.path.basename(seeded_db_src)}")
        except Exception as e:
            print(f"[DB] Warning: Failed to copy seeded DB: {e}")

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

    # Seed packages only if table is empty (fallback if seed file missing or empty)
    cursor.execute("SELECT COUNT(*) FROM packages")
    if cursor.fetchone()[0] == 0:
        print("[DB] Seeding packages from internal data...")
        _seed_packages(cursor)
    else:
        print("[DB] Database already contains package data.")

    conn.commit()
    conn.close()
    print("[DB] Database initialisation complete.")


def _seed_packages(cursor):
    """Insert initial holiday package data."""
    packages = [
        # --- ASIA ---
        ("Bali Bliss", "Bali, Indonesia", "7 nights / 8 days", 899.00, "Enjoy Ubud temples, rice terraces, and Seminyak beaches in Asia. Includes hotel & breakfast."),
        ("Maldives Dream Escape", "Maldives", "5 nights / 6 days", 1499.00, "Overwater bungalow, snorkelling, sunset cruises in Asia. All-inclusive luxury package."),
        ("Thailand Adventure", "Bangkok & Phuket, Thailand", "8 nights / 9 days", 749.00, "Street food tours in Bangkok, island hopping in Phuket, Asia. Budget-friendly & action-packed."),
        ("Sri Lanka Heritage", "Colombo, Kandy & Sigiriya", "6 nights / 7 days", 599.00, "Explore ancient ruins, tea plantations, and wildlife safaris in Asia. A cultural deep dive."),
        ("Tokyo Tech & Tradition", "Tokyo & Kyoto, Japan", "10 nights / 11 days", 2100.00, "Experience the neon lights of Shinjuku and the serene temples of Kyoto in Asia. JR Pass included."),
        ("Himalayan Heights", "Kathmandu & Pokhara, Nepal", "9 nights / 10 days", 1150.00, "Trekking in the Annapurna range, temple visits, and mountain flight to see Everest in Asia."),
        ("Vietnam Discovery", "Hanoi & Ha Long Bay, Vietnam", "8 nights / 9 days", 950.00, "Cruise through limestone karsts, explore ancient streets, and enjoy world-class street food in Asia."),
        ("Singapore City Lights", "Singapore", "4 nights / 5 days", 1250.00, "Gardens by the Bay, Sentosa Island, and Marina Bay Sands experience in Asia."),
        
        # --- EUROPE ---
        ("European Explorer (Europe)", "Paris, Rome, Barcelona", "12 nights / 13 days", 2299.00, "Three iconic cities in one trip across Europe. Guided tours, 4-star hotels, and airport transfers."),
        ("Swiss Alps Retreat", "Interlaken & Zermatt, Switzerland", "6 nights / 7 days", 2800.00, "Mountain railways, fondue evenings, and breathtaking views of the Matterhorn in Europe."),
        ("Greek Island Hopping", "Athens, Santorini & Mykonos", "10 nights / 11 days", 1850.00, "Ancient history in Athens followed by sunsets and white-washed villages in the Cyclades, Europe."),
        ("Icelandic Fire & Ice", "Reykjavik, Iceland", "5 nights / 6 days", 1600.00, "Blue Lagoon, Northern Lights hunting, and the Golden Circle waterfalls and geysers in Europe."),
        ("Italian Foodie Tour", "Florence & Bologna, Italy", "7 nights / 8 days", 1950.00, "Wine tasting in Tuscany and pasta making classes in the culinary heart of Italy, Europe."),
        ("London & Edinburgh", "UK", "8 nights / 9 days", 1750.00, "Royal palaces, historic castles, and the scenic train ride through the English countryside in Europe."),
        ("Amsterdam Canals", "Netherlands", "4 nights / 5 days", 850.00, "Bicycle tours, art museums, and romantic canal cruises in Europe."),
        
        # --- AMERICAS ---
        ("New York City Pulse", "New York, USA", "5 nights / 6 days", 1350.00, "Times Square, Central Park, Broadway shows, and Top of the Rock views in America."),
        ("Grand Canyon Adventure", "Arizona, USA", "6 nights / 7 days", 1100.00, "Hiking, helicopter tours, and camping under the stars in the National Park, America."),
        ("Rio Carnival Spirit", "Rio de Janeiro, Brazil", "7 nights / 8 days", 1450.00, "Christ the Redeemer, Copacabana beach, and vibrant samba nightlife in South America."),
        ("Inca Trail Trek", "Cusco & Machu Picchu, Peru", "9 nights / 10 days", 1900.00, "A bucket-list journey through the Andes to the lost city of the Incas in South America."),
        ("Canadian Rockies", "Banff & Jasper, Canada", "8 nights / 9 days", 2300.00, "Turquoise lakes, glaciers, and wildlife spotting in North America's most stunning mountains."),
        ("Costa Rica Eco-Tour", "San Jose, Costa Rica", "10 nights / 11 days", 1550.00, "Rainforest zip-lining, volcanic hot springs, and sloth spotting in Central America."),
        
        # --- AFRICA & MIDDLE EAST ---
        ("Dubai Luxury Getaway", "Dubai, UAE", "4 nights / 5 days", 1199.00, "Burj Khalifa, desert safari, luxury shopping, and fine dining experience in the Middle East."),
        ("Egyptian Pyramids", "Cairo & Luxor, Egypt", "7 nights / 8 days", 1200.00, "The Great Pyramids, Sphinx, and a luxury cruise down the Nile River in Africa."),
        ("Serengeti Safari", "Tanzania", "6 nights / 7 days", 3200.00, "The Big Five, luxury tented camps, and the Great Migration experience in Africa."),
        ("Moroccan Medinas", "Marrakesh & Fez, Morocco", "8 nights / 9 days", 1350.00, "Spice markets, Sahara desert glamping, and intricate Moorish architecture in Africa."),
        ("Cape Town & Wine", "South Africa", "7 nights / 8 days", 1650.00, "Table Mountain, penguin colonies, and world-class vineyards in South Africa."),
        
        # --- OCEANIA ---
        ("Sydney & Great Barrier Reef", "Australia", "11 nights / 12 days", 2900.00, "Opera House, Bondi Beach, and snorkelling in the world's largest coral reef, Oceania."),
        ("New Zealand South Island", "Queenstown, New Zealand", "9 nights / 10 days", 2500.00, "Milford Sound cruise, bungee jumping, and Lord of the Rings filming locations in Oceania."),
        ("Fiji Island Paradise", "Fiji", "7 nights / 8 days", 1700.00, "Crystal clear waters, kava ceremonies, and ultimate relaxation in a private resort, Oceania.")
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
