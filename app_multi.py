from flask import Flask, render_template, g, request, url_for, redirect
import sqlite3
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "kjv.db"

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

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/", methods=["GET"])
def index():
    cur = get_db().cursor()
    cur.execute("SELECT id, name FROM KJV_books")
    books_raw = cur.fetchall()

    # get chapter count for each book
    cur.execute("SELECT book_id, MAX(chapter) FROM verses GROUP BY book_id")
    chapter_counts = {book_id: max_chapter for book_id, max_chapter in cur.fetchall()}

    books = []
    for book_id, name in books_raw:
        chapters = list(range(1, chapter_counts.get(book_id, 0) + 1))
        books.append({"id": book_id, "name": name, "chapters": chapters})

    # Get selected versions or default to KJV, CUV_SIM
    selected_versions = request.args.getlist("version")
    if not selected_versions:
        selected_versions = ["KJV", "CUV_SIM"]

    return render_template("index.html",
                           books=books,
                           available_versions=AVAILABLE_VERSIONS,
                           selected_versions=selected_versions)

@app.route("/book/<int:book_id>/chapter/<int:chapter_num>")
def show_chapter(book_id, chapter_num):
    cur = get_db().cursor()
    cur.execute("SELECT name FROM KJV_books WHERE id = ?", (book_id,))
    book_name = cur.fetchone()[0]

    # Get versions from query, default if not provided
    versions = request.args.getlist("version")
    if not versions:
        versions = ["KJV", "CUV_SIM"]

    version_texts = {}
    for v in versions:
        cur.execute("""
            SELECT verse, text FROM verses
            WHERE book_id = ? AND chapter = ? AND version = ?
            ORDER BY verse
        """, (book_id, chapter_num, v))
        version_texts[v] = cur.fetchall()

    # Use verse numbers from KJV if present, else any version
    base_version = "KJV" if "KJV" in version_texts and version_texts["KJV"] else next(iter(version_texts))
    verse_numbers = [row[0] for row in version_texts[base_version]]

    # Build list of rows for template
    verses_data = []
    for idx, verse_num in enumerate(verse_numbers):
        verse_row = {"verse": verse_num}
        for v in versions:
            verse_row[v] = version_texts[v][idx][1] if idx < len(version_texts[v]) else ""
        verses_data.append(verse_row)

    # To pass selected versions back to the book page
    version_query = [("version", v) for v in versions]

    return render_template("chapter_multi.html",
                           book_name=book_name,
                           chapter_num=chapter_num,
                           versions=versions,
                           verses_data=verses_data,
                           book_id=book_id,
                           version_query=version_query)

if __name__ == "__main__":
    app.run(debug=True)
