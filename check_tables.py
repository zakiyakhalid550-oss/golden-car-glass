from dotenv import load_dotenv
import os
import psycopg

load_dotenv()

conn = psycopg.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    SELECT tablename
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY tablename;
""")

print("TABLES:")
for row in cur.fetchall():
    print(row[0])

cur.close()
conn.close()
