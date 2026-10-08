import sqlite3
import os


def create_database():

    # Project folder ka path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Correct database location
    DATABASE_PATH = os.path.join(
        BASE_DIR,
        "Database",
        "golden_car_glass.db"
    )

    # Database folder agar exist nahi karta to create karo
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    # =========================================
    # BOOKINGS TABLE
    # =========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL,
            car_model TEXT NOT NULL,
            glass_type TEXT NOT NULL,
            date TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    # =========================================
    # CUSTOMERS TABLE
    # =========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mobile TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")