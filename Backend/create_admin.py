import os
import psycopg
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
from flask import Flask

load_dotenv()

app = Flask(__name__)
bcrypt = Bcrypt(app)

username = input("Enter new admin username: ").strip()
password = input("Enter new admin password: ").strip()

if not username or not password:
    print("Username and password cannot be empty.")
    exit()

hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

conn = psycopg.connect(os.environ["DATABASE_URL"])

cur = conn.cursor()

cur.execute(
    """
    INSERT INTO admins (username, password)
    VALUES (%s, %s)
    ON CONFLICT (username)
    DO UPDATE SET password = EXCLUDED.password
    """,
    (username, hashed_password)
)

conn.commit()

cur.close()
conn.close()

print("Admin account created/updated successfully!")
print(f"Username: {username}")