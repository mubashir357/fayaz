from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from flask_cors import CORS
import os

app = Flask(__name__)
app.secret_key = 'kkoverseas_secret'
CORS(app)

# PostgreSQL database configuration from Render
DB_CONFIG = {
    'host': 'dpg-d206677fte5s738gih50-a',
    'port': '5432',
    'dbname': 'kkoverseas_db',
    'user': 'kkoverseas_db_user',
    'password': '6oEcmnu3e4W5CUPpL3mIoVQ3uE0is5EV'
}

ADMIN_PHONE = "8522006007"
ADMIN_PASSWORD = "2004@07"

# ---------- Database Connection ----------
def get_db():
    return psycopg2.connect(**DB_CONFIG)

# ---------- Initialize Tables ----------
def init_db():
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS users (
                            phone TEXT PRIMARY KEY,
                            password TEXT NOT NULL
                        )""")
            c.execute("""CREATE TABLE IF NOT EXISTS applications (
                            id SERIAL PRIMARY KEY,
                            name TEXT, phone TEXT, email TEXT,
                            dob TEXT, gender TEXT, country TEXT,
                            qualification TEXT, score TEXT,
                            visa_status TEXT
                        )""")
            c.execute("""CREATE TABLE IF NOT EXISTS messages (
                            id SERIAL PRIMARY KEY,
                            name TEXT,
                            email TEXT,
                            message TEXT
                        )""")
            conn.commit()

init_db()

# ---------- Routes ----------
@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        if phone != ADMIN_PHONE:
            return "Unauthorized: Only admin allowed."
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                if c.fetchone():
                    return "Admin already registered. Please login."
                c.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (phone, password))
                conn.commit()
        session['phone'] = phone
        return redirect(url_for('admin_panel'))
    return render_template("admin_signup.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                if c.fetchone():
                    return "User already exists. Please login."
                c.execute("INSERT INTO users (phone, password) VALUES (%s, %s)", (phone, password))
                conn.commit()
        return redirect(url_for('login'))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("SELECT * FROM users WHERE phone = %s", (phone,))
                user = c.fetchone()
                if not user or user[1] != password:
                    return "Invalid credentials"
        session['phone'] = phone
        if phone == ADMIN_PHONE:
            return redirect(url_for('admin_panel'))
        return redirect(url_for('home'))
    return render_template("login.html")

@app.route("/home")
def home():
    if 'phone' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

@app.route("/application", methods=["GET", "POST"])
def application():
    if 'phone' not in session:
        return redirect(url_for('login'))
    if request.method == "POST":
        data = (
            request.form['name'],
            request.form['phone'],
            request.form['email'],
            request.form['dob'],
            request.form['gender'],
            request.form['country'],
            request.form['qualification'],
            request.form['score'],
            request.form['visa_status']
        )
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("""INSERT INTO applications 
                            (name, phone, email, dob, gender, country, qualification, score, visa_status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", data)
                conn.commit()
        return redirect(url_for('home'))
    return render_template("application.html")

@app.route("/admin")
def admin_panel():
    if 'phone' not in session or session['phone'] != ADMIN_PHONE:
        return "Unauthorized"
    with get_db() as conn:
        with conn.cursor() as c:
            c.execute("SELECT * FROM applications")
            data = c.fetchall()
    return render_template("admin_panel.html", applications=data)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        with get_db() as conn:
            with conn.cursor() as c:
                c.execute("INSERT INTO messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
                conn.commit()
        return redirect(url_for('contact'))
    return render_template("contact.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- Run App (for Render or local) ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
