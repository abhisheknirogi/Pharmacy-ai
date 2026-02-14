import sqlite3

conn = sqlite3.connect("pharmacy.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    batch_no TEXT,
    quantity INTEGER,
    expiry_date TEXT,
    distributor TEXT
)
""")

conn.commit()
