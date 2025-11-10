import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "temmie.db")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tag_series (
    user_id INTEGER NOT NULL,
    tag TEXT NOT NULL,
    series TEXT NOT NULL,
    PRIMARY KEY (user_id, tag, series),
    FOREIGN KEY (user_id) REFERENCES user (id)
    FOREIGN KEY (series) REFERENCES series (name)
);
""")
print("✅ Table 'tag_series' ensured.")

conn.commit()
conn.close()
