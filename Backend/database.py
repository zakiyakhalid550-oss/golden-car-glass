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

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("Database created successfully!")