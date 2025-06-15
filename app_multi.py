from flask import Flask, render_template, request
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB = Path(__file__).with_name("kjv.db")

VERSIONS = [
    ("KJV", "King James Version"),
    ("CUV_SIM", "Simplified Chinese"),
    ("CUV_TRAD", "Traditional Chinese"),
    ("YLT", "Young's Literal Translation"),
]
DEFAULT = ["KJV", "CUV_SIM"]

def get_db():
    return sqlite3.connect(DB)

@app.route("/")
def index():
    db = get_db()
    books = db.execute("SELECT id, name FROM KJV_books").fetchall()
    db.close()
    return render_template("book.html", books=books, versions=VERSIONS, selected=request.args.getlist("version") or DEFAULT)

@app.route("/chapter")
def chapter():
    book_id = int(request.args["book_id"]); ch = int(request.args["chapter"])
    sel = request.args.getlist("version") or DEFAULT
    db = get_db()
    bname = db.execute("SELECT name FROM KJV_books WHERE id=?", (book_id,)).fetchone()[0]
    verses_data = {v: db.execute("SELECT verse,text FROM verses WHERE book_id=? AND chapter=? AND version=? ORDER BY verse",(book_id,ch,v)).fetchall() for v,_ in VERSIONS if v in sel}
    db.close()
    verses = [row[0] for row in next(iter(verses_data.values()))]
    return render_template("chapter_multi.html", book_name=bname, chapter=ch, verses=verses, verse_count=len(verses), verses_data=verses_data, selected=sel)

if __name__ == "__main__":
    app.run(debug=True)
