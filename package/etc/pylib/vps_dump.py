import sqlite3
import os

db_path = "/var/lib/syslog-ng/vps.sqlite"

if not os.path.exists(db_path):
    raise FileNotFoundError(f"Database file not found at {db_path}")

try:
    with sqlite3.connect(db_path) as db:
        cursor = db.cursor()

        # Ensure the table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                host TEXT PRIMARY KEY,
                fields TEXT
            )
        """)

        cursor.execute("SELECT host, fields FROM hosts")
        rows = cursor.fetchall()
        for k, v in rows:
            print(f"key={k}={v}")

except sqlite3.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
