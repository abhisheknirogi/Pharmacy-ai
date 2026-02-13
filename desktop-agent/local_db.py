import sqlite3

conn = sqlite3.connect("agent_cache.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS pending_files(
    id INTEGER PRIMARY KEY,
    path TEXT,
    uploaded INTEGER DEFAULT 0
)
""")
conn.commit()
