import sqlite3
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

connection = sqlite3.connect("../Database/golden_car_glass.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS admins(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

username = input("Enter admin username: ")
password = input("Enter admin password: ")

hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

# Check if admin already exists
cursor.execute(
    "SELECT id FROM admins WHERE username = ?",
    (username,)
)

existing_admin = cursor.fetchone()

if existing_admin:

    cursor.execute(
        "UPDATE admins SET password = ? WHERE username = ?",
        (hashed_password, username)
    )

    print("Admin password updated successfully!")

else:

    cursor.execute(
        "INSERT INTO admins(username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    print("Admin created successfully!")

connection.commit()
connection.close()