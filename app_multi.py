from flask import Flask, render_template, g, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "kjv.db"
MY_NOTES_DB = BASE_DIR / "my_note.db"

AVAILABLE_VERSIONS = [
    ("KJV", "King James Version"),
    ("CUV_SIM", "Simplified Chinese"),
    ("CUV_TRAD", "Traditional Chinese"),
    ("YLT", "Young's Literal Translation")
]

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def get_notes_db():
    db = getattr(g, "_my_notes_db", None)
    if db is None:
        db = g._my_notes_db = sqlite3.connect(MY_NOTES_DB)
        db.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                book_id INTEGER,
                chapter INTEGER,
                verse INTEGER,
                note TEXT,
                PRIMARY KEY (book_id, chapter, verse)
            )
        """)
        db.commit()
    return db

@app.teardown_appcontext
def close_connections(exception):
    db = getattr(g, "_my_notes_db", None)
    if db is not None:
        db.close()
    db2 = getattr(g, "_database", None)
    if db2 is not None:
        db2.close()

@app.route("/", methods=["GET"])
def index():
    cur = get_db().cursor()
    cur.execute("SELECT id, name FROM KJV_books")
    books = cur.fetchall()
    cur.execute("SELECT book_id, MAX(chapter) FROM verses GROUP BY book_id")
    chapter_counts = {book_id: max_chapter for book_id, max_chapter in cur.fetchall()}

    # List of dicts: each book's id, name, and chapters
    book_objs = []
    for book_id, name in books:
        chapters = list(range(1, chapter_counts.get(book_id, 0) + 1))
        book_objs.append({"id": book_id, "name": name, "chapters": chapters})

    selected_versions = request.args.getlist("version")
    if not selected_versions:
        selected_versions = ["KJV", "CUV_SIM"]

    return render_template(
        "index.html",
        books=book_objs,
        available_versions=AVAILABLE_VERSIONS,
        selected_versions=selected_versions
    )

@app.route("/book/<int:book_id>/chapter/<int:chapter_num>")
def show_chapter(book_id, chapter_num):
    cur = get_db().cursor()
    cur.execute("SELECT name FROM KJV_books WHERE id = ?", (book_id,))
    book_name = cur.fetchone()[0] if cur.rowcount != 0 else "Unknown Book"

    versions = request.args.getlist("version")
    if not versions:
        versions = ["KJV", "CUV_SIM"]

    # Gather all verse numbers in this chapter
    cur.execute("SELECT DISTINCT verse FROM verses WHERE book_id = ? AND chapter = ? ORDER BY verse", (book_id, chapter_num))
    verse_numbers = [row[0] for row in cur.fetchall()]

    # Get verse texts for each selected version
    version_texts = {}
    for v in versions:
        cur.execute("""
            SELECT verse, text FROM verses
            WHERE book_id = ? AND chapter = ? AND version = ?
            ORDER BY verse
        """, (book_id, chapter_num, v))
        rows = cur.fetchall()
        # Dictionary: verse_number -> text
        version_texts[v] = {verse: text for verse, text in rows}

    # Get user notes for this chapter
    notes_db = get_notes_db()
    notes_cursor = notes_db.cursor()
    notes_cursor.execute(
        "SELECT verse, note FROM notes WHERE book_id = ? AND chapter = ?", (book_id, chapter_num)
    )
    notes = {verse: note for verse, note in notes_cursor.fetchall()}

    # Build verse_row list
    verse_rows = []
    for verse in verse_numbers:
        row = {"verse": verse}
        for v in versions:
            row[v] = version_texts.get(v, {}).get(verse, "")
        row["note"] = notes.get(verse, "")
        verse_rows.append(row)

    return render_template(
        "chapter_multi.html",
        book_id=book_id,
        book_name=book_name,
        chapter_num=chapter_num,
        versions=versions,
        verse_rows=verse_rows
    )

@app.route("/save_note", methods=["POST"])
def save_note():
    data = request.get_json()
    book_id = int(data["book_id"])
    chapter = int(data["chapter"])
    verse = int(data["verse"])
    note = data["note"]

    db = get_notes_db()
    c = db.cursor()
    c.execute("""
        INSERT INTO notes (book_id, chapter, verse, note)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(book_id, chapter, verse) DO UPDATE SET note=excluded.note
    """, (book_id, chapter, verse, note))
    db.commit()
    return jsonify(success=True)

if __name__ == "__main__":
    app.run(debug=True)
