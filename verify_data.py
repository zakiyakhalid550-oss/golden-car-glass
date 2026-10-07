from dotenv import load_dotenv
import os
import psycopg

load_dotenv()

conn = psycopg.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

for table in ["bookings", "booking_photos", "admins"]:
    cur.execute(f"SELECT COUNT(*) FROM public.{table}")
    print(f"{table}: {cur.fetchone()[0]}")

cur.execute("SELECT id, booking_id FROM public.booking_photos ORDER BY id")
print("PHOTO RECORDS:")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
