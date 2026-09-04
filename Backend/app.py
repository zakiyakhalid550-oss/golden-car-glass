from datetime import date as datetime_date

from flask import Flask, render_template, request, redirect, session, url_for, make_response
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from functools import wraps
import sqlite3
import os
import time


# =========================================================
# APP SETUP
# =========================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.path.join(
    BASE_DIR,
    "Database",
    "golden_car_glass.db"
)

os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

app = Flask(
    __name__,
    template_folder="../Frontend"
)

csrf = CSRFProtect(app)


# =========================================================
# SECRET KEY
# =========================================================
load_dotenv()

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "dev-change-this-before-production"
)


# =========================================================
# SESSION SECURITY
# =========================================================

app.config["PERMANENT_SESSION_LIFETIME"] = 1800
app.config["SESSION_REFRESH_EACH_REQUEST"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Local development ke liye False
# Production HTTPS par True karna
app.config["SESSION_COOKIE_SECURE"] = False


bcrypt = Bcrypt(app)


# =========================================================
# LOGIN SECURITY
# =========================================================

MAX_LOGIN_ATTEMPTS = 5

# 5 minutes
LOCKOUT_TIME = 300


# =========================================================
# DATABASE
# =========================================================

def get_db_connection():

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection

# =========================================================
# DATABASE INITIALIZATION
# =========================================================

def initialize_database():

    connection = sqlite3.connect(DATABASE_PATH)

    cursor = connection.cursor()

    # Create bookings table if it does not exist
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

    # Create admins table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

initialize_database()

# =========================================================
# LOGIN REQUIRED
# =========================================================

def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):

        if "admin_id" not in session or "username" not in session:

            session.clear()

            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# BOOKING
# =========================================================

# =========================================================
# BOOKING
# =========================================================

@app.route("/book", methods=["POST"])
def book():

    name = request.form.get("name", "").strip()
    mobile = request.form.get("mobile", "").strip()
    car_model = request.form.get("car_model", "").strip()
    glass_type = request.form.get("glass_type", "").strip()
    date = request.form.get("date", "").strip()
    message = request.form.get("message", "").strip()


    # =========================================================
    # BASIC INPUT VALIDATION
    # =========================================================

    if not name:
        return "Please enter your name.", 400

    if not mobile:
        return "Please enter your mobile number.", 400

    if not car_model:
        return "Please enter your car model.", 400

    if not glass_type:
        return "Please select a glass type.", 400

    if not date:
        return "Please select a booking date.", 400



    try:
        booking_date = datetime_date.fromisoformat(date)
    except ValueError:
        return "Invalid booking date.", 400

    if booking_date < datetime_date.today():
        return "Booking date cannot be in the past.", 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO bookings
        (
            name,
            mobile,
            car_model,
            glass_type,
            date,
            message,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        mobile,
        car_model,
        glass_type,
        date,
        message,
        "Pending"
    ))

    connection.commit()

    booking_id = cursor.lastrowid

    connection.close()

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Booking Confirmed</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            text-align: center;
            padding-top: 100px;
        }}

        .success-box {{
            background: white;
            width: 450px;
            max-width: 90%;
            margin: auto;
            padding: 35px;
            border-radius: 12px;
            box-shadow: 0 0 15px rgba(0,0,0,0.15);
        }}

        .success-icon {{
            font-size: 55px;
        }}

        h1 {{
            color: #198754;
        }}

        .booking-id {{
            background-color: #fff3cd;
            padding: 12px;
            border-radius: 6px;
            font-size: 20px;
            font-weight: bold;
            margin: 20px 0;
        }}

        .home-btn {{
            display: inline-block;
            background-color: #222;
            color: white;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
        }}

        .home-btn:hover {{
            background-color: #444;
        }}
    </style>
</head>

<body>

    <div class="success-box">

        <div class="success-icon">✅</div>

        <h1>Booking Submitted Successfully!</h1>

        <p>
            Your booking has been received successfully.
        </p>

        <div class="booking-id">
            Booking Reference: #{booking_id}
        </div>

        <p>
            Our team will contact you soon.
        </p>

        <a href="/" class="home-btn">
            🏠 Back to Home
        </a>

    </div>

</body>
</html>
""".replace("{{ booking_id }}", str(booking_id))


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        # -------------------------------------------------
        # CURRENT TIME
        # -------------------------------------------------

        current_time = time.time()

        # -------------------------------------------------
        # PREVIOUS FAILED ATTEMPTS
        # -------------------------------------------------

        attempts = session.get(
            "login_attempts",
            0
        )

        lock_time = session.get(
            "login_lock_time",
            0
        )

        # -------------------------------------------------
        # CHECK LOCK
        # -------------------------------------------------

        if attempts >= MAX_LOGIN_ATTEMPTS:

            if current_time - lock_time < LOCKOUT_TIME:

                remaining = int(
                    LOCKOUT_TIME -
                    (current_time - lock_time)
                )

                return (
                    f"Too many failed attempts. "
                    f"Try again after {remaining} seconds."
                ), 429

            # Lock expired
            session["login_attempts"] = 0

            session.pop(
                "login_lock_time",
                None
            )

            attempts = 0

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        try:

            cursor = connection.cursor()

            cursor.execute(
                "SELECT id, username, password "
                "FROM admins "
                "WHERE username = ?",
                (username,)
            )

            admin = cursor.fetchone()

        finally:

            connection.close()

        # -------------------------------------------------
        # CORRECT LOGIN
        # -------------------------------------------------

        if admin:

            password_correct = bcrypt.check_password_hash(
                admin["password"],
                password
            )

        else:

            password_correct = False

        if password_correct:

            # Clear failed attempts
            session.pop(
                "login_attempts",
                None
            )

            session.pop(
                "login_lock_time",
                None
            )

            # Permanent session
            session.permanent = True

            # Save admin information
            session["admin_id"] = admin["id"]

            session["username"] = admin["username"]

            return redirect(
                url_for("bookings")
            )

        # -------------------------------------------------
        # WRONG LOGIN
        # -------------------------------------------------

        attempts += 1

        session["login_attempts"] = attempts

        # Lock after 5 failed attempts
        if attempts >= MAX_LOGIN_ATTEMPTS:

            session["login_lock_time"] = current_time

            return (
                "Too many failed attempts. "
                "Login locked for 5 minutes."
            )

        remaining_attempts = (
            MAX_LOGIN_ATTEMPTS - attempts
        )

        return (
            "Invalid Username or Password. "
            f"{remaining_attempts} attempts remaining."
        )

    # GET request
    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# =========================================================
# BOOKINGS
# =========================================================

# ---------------- BOOKINGS ---------------- #

@app.route("/bookings")
@login_required
def bookings():

    connection = get_db_connection()
    cursor = connection.cursor()

    # All bookings
    cursor.execute("""
        SELECT * FROM bookings
        ORDER BY date ASC
    """)
    bookings = cursor.fetchall()

    # Total bookings
    total_bookings = len(bookings)

    # Pending
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = ?",
        ("Pending",)
    )
    pending_bookings = cursor.fetchone()[0]

    # In Progress
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = ?",
        ("In Progress",)
    )
    in_progress_bookings = cursor.fetchone()[0]

    # Completed
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = ?",
        ("Completed",)
    )
    completed_bookings = cursor.fetchone()[0]

    # Cancelled
    cursor.execute(
        "SELECT COUNT(*) FROM bookings WHERE status = ?",
        ("Cancelled",)
    )
    cancelled_bookings = cursor.fetchone()[0]

    connection.close()

    response = make_response(
        render_template(
            "bookings.html",
            bookings=bookings,
            total_bookings=total_bookings,
            pending_bookings=pending_bookings,
            in_progress_bookings=in_progress_bookings,
            completed_bookings=completed_bookings,
            cancelled_bookings=cancelled_bookings
        )
    )

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )

    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# =========================================================
# UPDATE STATUS
# =========================================================

@app.route(
    "/update_status/<int:id>",
    methods=["POST"]
)
@login_required
def update_status(id):

    status = request.form.get(
        "status",
        ""
    ).strip()


    # Allowed statuses
    allowed_statuses = [
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled"
    ]


    # -------------------------------------------------
    # VALIDATE STATUS
    # -------------------------------------------------

    if status not in allowed_statuses:

        return (
            "Invalid booking status.",
            400
        )


    # -------------------------------------------------
    # UPDATE DATABASE
    # -------------------------------------------------

    connection = get_db_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE bookings
        SET status = ?
        WHERE id = ?
        """,
        (
            status,
            id
        )
    )


    connection.commit()

    connection.close()


    # -------------------------------------------------
    # IMPORTANT
    # -------------------------------------------------
    # AJAX fetch ke liye redirect allowed hai.
    # Browser page reload nahi karega because
    # JavaScript fetch use kar raha hai.

    return redirect(
        url_for("bookings")
    )


# =========================================================
# VIEW BOOKING DETAILS
# =========================================================

@app.route("/booking/<int:id>")
@login_required
def view_booking(id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE id = ?",
        (id,)
    )

    booking = cursor.fetchone()

    connection.close()

    if not booking:
        return "Booking not found.", 404

    return render_template(
        "booking_details.html",
        booking=booking
    )


# =========================================================
# TRACK BOOKING
# =========================================================

@app.route("/track_booking", methods=["GET", "POST"])
def track_booking():

    if request.method == "POST":

        booking_id = request.form.get(
            "booking_id",
            ""
        ).strip()

        if not booking_id.isdigit():
            return "Invalid Booking Reference.", 400

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM bookings WHERE id = ?",
            (int(booking_id),)
        )

        booking = cursor.fetchone()

        connection.close()

        if not booking:
            return "Booking not found.", 404

        return render_template(
            "booking_details.html",
            booking=booking
        )

    return render_template("track_booking.html")
@app.route(
    "/delete/<int:id>",
    methods=["POST"]
)
@login_required
def delete_booking(id):
    connection = get_db_connection()

    cursor = connection.cursor()


    # -------------------------------------------------
    # CHECK BOOKING
    # -------------------------------------------------

    cursor.execute(
        """
        SELECT id
        FROM bookings
        WHERE id = ?
        """,
        (id,)
    )


    booking = cursor.fetchone()


    # Booking not found
    if not booking:

        connection.close()

        return (
            "Booking not found.",
            404
        )


    # -------------------------------------------------
    # DELETE
    # -------------------------------------------------

    cursor.execute(
        """
        DELETE FROM bookings
        WHERE id = ?
        """,
        (id,)
    )


    connection.commit()

    connection.close()


    return redirect(
        url_for("bookings")
    )

# =========================================================
# ERROR HANDLING
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Page Not Found</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding-top: 100px;
            }

            .error-box {
                background: white;
                width: 450px;
                max-width: 90%;
                margin: auto;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 0 15px rgba(0,0,0,0.15);
            }

            .error-icon {
                font-size: 55px;
            }

            h1 {
                color: #c99a00;
            }

            .home-btn {
                display: inline-block;
                background-color: #222;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }

            .home-btn:hover {
                background-color: #444;
            }
        </style>
    </head>

    <body>

        <div class="error-box">

            <div class="error-icon">🔍</div>

            <h1>Page Not Found</h1>

            <p>
                Sorry, the page you are looking for does not exist.
            </p>

            <a href="/" class="home-btn">
                🏠 Back to Home
            </a>

        </div>

    </body>
    </html>
    """, 404

# =========================================================
# INTERNAL SERVER ERROR
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):

    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Something Went Wrong</title>

        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                text-align: center;
                padding-top: 100px;
            }

            .error-box {
                background: white;
                width: 450px;
                max-width: 90%;
                margin: auto;
                padding: 35px;
                border-radius: 12px;
                box-shadow: 0 0 15px rgba(0,0,0,0.15);
            }

            .error-icon {
                font-size: 55px;
            }

            h1 {
                color: #c99a00;
            }

            .home-btn {
                display: inline-block;
                background-color: #222;
                color: white;
                text-decoration: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }

            .home-btn:hover {
                background-color: #444;
            }
        </style>
    </head>

    <body>

        <div class="error-box">

            <div class="error-icon">⚠️</div>

            <h1>Something Went Wrong</h1>

            <p>
                Sorry, something went wrong on our side.
            </p>

            <p>
                Please try again later.
            </p>

            <a href="/" class="home-btn">
                🏠 Back to Home
            </a>

        </div>

    </body>
    </html>
    """, 500

# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    )
