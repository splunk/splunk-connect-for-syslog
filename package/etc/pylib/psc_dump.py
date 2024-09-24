import sqlite3
import os

db_path = "/var/lib/syslog-ng/hostip.sqlite"

if not os.path.exists(db_path):
    raise FileNotFoundError(f"Database file not found at {db_path}")

try:
    with sqlite3.connect(db_path) as db:
        cursor = db.cursor()

        # Ensure the table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hosts (
                ip_int INTEGER PRIMARY KEY,
                host TEXT
            )
        """)

        cursor.execute("SELECT ip_int, host FROM hosts")
        rows = cursor.fetchall()
        for k, v in rows:
            print(f"key={k}={v}")

except sqlite3.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
