import sqlite3
import os

# Use the persistent NFS database path
DB_PATH = '/nfs/demo.db'

# Check if the database exists
if not os.path.exists(DB_PATH):
    print(f"No DB found at {DB_PATH}. Nothing to clear.")
    raise SystemExit(0)

# Connect to the database and clear the parts table
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("DELETE FROM parts")
conn.commit()
conn.close()

print(f"Cleared all parts from the database at {DB_PATH}.")
