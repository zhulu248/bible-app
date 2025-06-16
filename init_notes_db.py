import sqlite3
from pathlib import Path

# Set path to the notes database
db_path = Path(__file__).resolve().parent / "my_notes.db"

# Connect to the database (creates it if it doesn't exist)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the notes table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        book_id INTEGER NOT NULL,
        chapter INTEGER NOT NULL,
        verse INTEGER NOT NULL,
        note TEXT,
        UNIQUE(book_id, chapter, verse)
    )
''')

# Commit and close
conn.commit()
conn.close()

print("✅ notes table created in my_notes.db")
