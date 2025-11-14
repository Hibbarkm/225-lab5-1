"""
Clear all rows from the parts table.
Run with: python data-clear.py
"""

import sqlite3
import os

DB_PATH = 'data/warehouse.db'
if not os.path.exists(DB_PATH):
    print(f"No DB found at {DB_PATH}. Nothing to clear.")
    raise SystemExit(0)

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("DELETE FROM parts")
conn.commit()
conn.close()

print("Cleared all parts from the database.")
