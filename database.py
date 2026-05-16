"""
database.py — SQLite helper for TravelMate chatbot
Handles: packages table, learned_responses table
"""

import sqlite3
import os
import sys

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
