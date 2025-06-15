# create_unified_table.py
import sqlite3

conn = sqlite3.connect("kjv.db")  # or your main .db
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS verses (
    book_id INTEGER,
    chapter INTEGER,
    verse INTEGER,
    version TEXT,
    text TEXT,
    PRIMARY KEY (book_id, chapter, verse, version)
)
""")

conn.commit()
conn.close()
print("Unified table created.")
