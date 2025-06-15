from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)
DATABASE = "kjv.db"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    cur = get_db().cursor()
    cur.execute("SELECT id, name FROM KJV_books")
    books = cur.fetchall()
    return render_template("index.html", books=books)

@app.route("/book/<int:book_id>")
def show_book(book_id):
    cur = get_db().cursor()
    cur.execute("SELECT DISTINCT chapter FROM KJV_verses WHERE book_id = ? ORDER BY chapter", (book_id,))
    chapters = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT name FROM KJV_books WHERE id = ?", (book_id,))
    book_name = cur.fetchone()[0]
    # print(f"Book ID: {book_id}, Name: {book_name}, Chapters: {chapters}")  # <--- this helps us debug
    return render_template("book.html", book_id=book_id, book_name=book_name, chapters=chapters)

@app.route("/book/<int:book_id>/chapter/<int:chapter_num>")
def show_chapter(book_id, chapter_num):
    cur = get_db().cursor()
    cur.execute("SELECT name FROM KJV_books WHERE id = ?", (book_id,))
    book_name = cur.fetchone()[0]
    cur.execute("""
        SELECT verse, text
        FROM KJV_verses
        WHERE book_id = ? AND chapter = ?
        ORDER BY verse
    """, (book_id, chapter_num))
    verses = cur.fetchall()
    return render_template("chapter.html", book_name=book_name, chapter_num=chapter_num, verses=verses)
