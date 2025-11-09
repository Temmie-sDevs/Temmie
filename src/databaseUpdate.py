import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "..", "database", "temmie.db")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Check if the column already exists
cursor.execute("PRAGMA table_info(user);")
columns = [col[1] for col in cursor.fetchall()]
if "mention" not in columns:
    cursor.execute("ALTER TABLE user ADD COLUMN mention BOOL NOT NULL DEFAULT 1;")
    print("✅ Column 'mention' added successfully.")
else:
    print("ℹ️ Column 'mention' already exists.")

conn.commit()
conn.close()
