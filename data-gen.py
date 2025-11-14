import sqlite3
import os

# Use the persistent NFS path
DB_PATH = '/nfs/demo.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Sample parts to populate the database
sample_parts = [
    ("Front Brake Rotor", 4, "Shelf A-1"),
    ("Air Filter (Sportster)", 12, "Shelf A-2"),
    ("Battery Cable", 6, "Bin 5"),
    ("Oil Filter", 25, "Shelf B-1"),
    ("Clutch Cable", 3, "Rack C"),
]

# Connect to the database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS parts (
    part_id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    location TEXT
)
""")

# Insert sample parts
c.executemany("INSERT INTO parts (part_name, quantity, location) VALUES (?, ?, ?)", sample_parts)
conn.commit()
conn.close()

print(f"Inserted {len(sample_parts)} sample parts into {DB_PATH}")
