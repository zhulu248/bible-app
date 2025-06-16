import sqlite3
conn = sqlite3.connect('notes.db')
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS notes (
    book_id INTEGER,
    chapter INTEGER,
    verse INTEGER,
    note TEXT,
    PRIMARY KEY (book_id, chapter, verse)
)
''')
conn.commit()
conn.close()
