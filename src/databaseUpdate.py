import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "temmie.db")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# --- Ensure 'user_tags' table exists ---
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_tags (
        user_id INTEGER NOT NULL,
        tag TEXT NOT NULL,
        PRIMARY KEY (user_id, tag),
        FOREIGN KEY (user_id) REFERENCES user (id)
    );
""")
print("✅ Table 'user_tags' ensured.")

conn.commit()
conn.close()
