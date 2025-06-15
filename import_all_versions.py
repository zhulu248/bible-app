# import_all_versions.py
import sqlite3

# Each entry: (version_code, path_to_db, verse_table_name)
version_sources = [
    ("KJV", "KJV.db", "KJV_verses"),
    ("CUV_SIM", "ChiSB.db", "ChiSB_verses"),
    ("CUV_TRAD", "ChiUnL.db", "ChiUnL_verses"),
    ("CUV_MIX", "ChiUn.db", "ChiUn_verses"),
    ("ACV", "ACV.db", "ACV_verses"),
    ("DARBY", "Darby.db", "Darby_verses"),
    ("YLT", "YLT.db", "YLT_verses"),
]

# Connect to master unified DB
master_conn = sqlite3.connect("kjv.db")
master_cur = master_conn.cursor()

for version, db_path, table in version_sources:
    print(f"Importing {version} from {db_path}...")

    src_conn = sqlite3.connect(db_path)
    src_cur = src_conn.cursor()

    src_cur.execute(f"SELECT book_id, chapter, verse, text FROM {table}")
    rows = src_cur.fetchall()

    master_cur.executemany(
        "INSERT OR REPLACE INTO verses (book_id, chapter, verse, version, text) VALUES (?, ?, ?, ?, ?)",
        [(b, c, v, version, t) for (b, c, v, t) in rows]
    )

    src_conn.close()
    print(f" → {len(rows)} rows inserted from {version}.")

master_conn.commit()
master_conn.close()
print("✅ All versions imported into unified table.")
