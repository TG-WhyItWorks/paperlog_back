import sqlite3
conn = sqlite3.connect("your_database.db")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS alembic_version;")
conn.commit()
conn.close()