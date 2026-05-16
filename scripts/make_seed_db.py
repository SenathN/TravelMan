"""
Generate a clean seeded SQLite database for TravelMate.
This file creates data/seed_chatbot.db with only the initial package seed data.
"""
import os
import sqlite3

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DB_PATH = os.path.abspath(os.path.join(DATA_DIR, 'seed_chatbot.db'))

os.makedirs(DATA_DIR, exist_ok=True)

packages = [
    ("Bali Bliss", "Bali, Indonesia", "7 nights / 8 days", 899.00, "Enjoy Ubud temples, rice terraces, and Seminyak beaches in Asia. Includes hotel & breakfast."),
    ("Maldives Dream Escape", "Maldives", "5 nights / 6 days", 1499.00, "Overwater bungalow, snorkelling, sunset cruises in Asia. All-inclusive luxury package."),
    ("Thailand Adventure", "Bangkok & Phuket, Thailand", "8 nights / 9 days", 749.00, "Street food tours in Bangkok, island hopping in Phuket, Asia. Budget-friendly & action-packed."),
    ("Sri Lanka Heritage", "Colombo, Kandy & Sigiriya", "6 nights / 7 days", 599.00, "Explore ancient ruins, tea plantations, and wildlife safaris in Asia. A cultural deep dive."),
    ("Tokyo Tech & Tradition", "Tokyo & Kyoto, Japan", "10 nights / 11 days", 2100.00, "Experience the neon lights of Shinjuku and the serene temples of Kyoto in Asia. JR Pass included."),
    ("Himalayan Heights", "Kathmandu & Pokhara, Nepal", "9 nights / 10 days", 1150.00, "Trekking in the Annapurna range, temple visits, and mountain flight to see Everest in Asia."),
    ("Vietnam Discovery", "Hanoi & Ha Long Bay, Vietnam", "8 nights / 9 days", 950.00, "Cruise through limestone karsts, explore ancient streets, and enjoy world-class street food in Asia."),
    ("Singapore City Lights", "Singapore", "4 nights / 5 days", 1250.00, "Gardens by the Bay, Sentosa Island, and Marina Bay Sands experience in Asia."),
    ("European Explorer (Europe)", "Paris, Rome, Barcelona", "12 nights / 13 days", 2299.00, "Three iconic cities in one trip across Europe. Guided tours, 4-star hotels, and airport transfers."),
    ("Swiss Alps Retreat", "Interlaken & Zermatt, Switzerland", "6 nights / 7 days", 2800.00, "Mountain railways, fondue evenings, and breathtaking views of the Matterhorn in Europe."),
    ("Greek Island Hopping", "Athens, Santorini & Mykonos", "10 nights / 11 days", 1850.00, "Ancient history in Athens followed by sunsets and white-washed villages in the Cyclades, Europe."),
    ("Icelandic Fire & Ice", "Reykjavik, Iceland", "5 nights / 6 days", 1600.00, "Blue Lagoon, Northern Lights hunting, and the Golden Circle waterfalls and geysers in Europe."),
    ("Italian Foodie Tour", "Florence & Bologna, Italy", "7 nights / 8 days", 1950.00, "Wine tasting in Tuscany and pasta making classes in the culinary heart of Italy, Europe."),
    ("London & Edinburgh", "UK", "8 nights / 9 days", 1750.00, "Royal palaces, historic castles, and the scenic train ride through the English countryside in Europe."),
    ("Amsterdam Canals", "Netherlands", "4 nights / 5 days", 850.00, "Bicycle tours, art museums, and romantic canal cruises in Europe."),
    ("New York City Pulse", "New York, USA", "5 nights / 6 days", 1350.00, "Times Square, Central Park, Broadway shows, and Top of the Rock views in America."),
    ("Grand Canyon Adventure", "Arizona, USA", "6 nights / 7 days", 1100.00, "Hiking, helicopter tours, and camping under the stars in the National Park, America."),
    ("Rio Carnival Spirit", "Rio de Janeiro, Brazil", "7 nights / 8 days", 1450.00, "Christ the Redeemer, Copacabana beach, and vibrant samba nightlife in South America."),
    ("Inca Trail Trek", "Cusco & Machu Picchu, Peru", "9 nights / 10 days", 1900.00, "A bucket-list journey through the Andes to the lost city of the Incas in South America."),
    ("Canadian Rockies", "Banff & Jasper, Canada", "8 nights / 9 days", 2300.00, "Turquoise lakes, glaciers, and wildlife spotting in North America's most stunning mountains."),
    ("Costa Rica Eco-Tour", "San Jose, Costa Rica", "10 nights / 11 days", 1550.00, "Rainforest zip-lining, volcanic hot springs, and sloth spotting in Central America."),
    ("Dubai Luxury Getaway", "Dubai, UAE", "4 nights / 5 days", 1199.00, "Burj Khalifa, desert safari, luxury shopping, and fine dining experience in the Middle East."),
    ("Egyptian Pyramids", "Cairo & Luxor, Egypt", "7 nights / 8 days", 1200.00, "The Great Pyramids, Sphinx, and a luxury cruise down the Nile River in Africa."),
    ("Serengeti Safari", "Tanzania", "6 nights / 7 days", 3200.00, "The Big Five, luxury tented camps, and the Great Migration experience in Africa."),
    ("Moroccan Medinas", "Marrakesh & Fez, Morocco", "8 nights / 9 days", 1350.00, "Spice markets, Sahara desert glamping, and intricate Moorish architecture in Africa."),
    ("Cape Town & Wine", "South Africa", "7 nights / 8 days", 1650.00, "Table Mountain, penguin colonies, and world-class vineyards in South Africa."),
    ("Sydney & Great Barrier Reef", "Australia", "11 nights / 12 days", 2900.00, "Opera House, Bondi Beach, and snorkelling in the world's largest coral reef, Oceania."),
    ("New Zealand South Island", "Queenstown, New Zealand", "9 nights / 10 days", 2500.00, "Milford Sound cruise, bungee jumping, and Lord of the Rings filming locations in Oceania."),
    ("Fiji Island Paradise", "Fiji", "7 nights / 8 days", 1700.00, "Crystal clear waters, kava ceremonies, and ultimate relaxation in a private resort, Oceania.")
]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    destination TEXT NOT NULL,
    duration TEXT NOT NULL,
    price_usd REAL NOT NULL,
    description TEXT
)
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS learned_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL UNIQUE,
    answer TEXT NOT NULL
)
""")
cur.execute("DELETE FROM packages")
cur.execute("DELETE FROM learned_responses")
cur.executemany(
    "INSERT INTO packages (name, destination, duration, price_usd, description) VALUES (?, ?, ?, ?, ?)",
    packages
)
conn.commit()
conn.close()
print(f"Seed DB generated: {DB_PATH} ({len(packages)} packages)")
