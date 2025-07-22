from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'kkoverseas_secret'
CORS(app)

DB_NAME = "kk_overseas.db"

ADMIN_PHONE = "8522006007"
ADMIN_PASSWORD = "2004@07"

# ------------------ Initialize Database ------------------
def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
                        phone TEXT PRIMARY KEY,
                        password TEXT NOT NULL
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS applications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, phone TEXT, email TEXT,
                        dob TEXT, gender TEXT, country TEXT,
                        qualification TEXT, score TEXT,
                        visa_status TEXT
                    )""")
        c.execute("""CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        email TEXT,
                        message TEXT
                    )""")
        conn.commit()

init_db()

# ------------------ Index Redirect ------------------
@app.route("/")
def index():
    return redirect(url_for('login'))

# ------------------ Admin Signup ------------------
@app.route("/admin-signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        if phone != ADMIN_PHONE:
            return "Unauthorized: Only admin allowed."
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            if c.fetchone():
                return "Admin already registered. Please login."
            c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
            conn.commit()
        session['phone'] = phone
        return redirect(url_for('admin_panel'))
    return render_template("admin_signup.html")

# ------------------ General Signup ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            if c.fetchone():
                return "User already exists. Please login."
            c.execute("INSERT INTO users (phone, password) VALUES (?, ?)", (phone, password))
            conn.commit()
        return redirect(url_for('login'))
    return render_template("signup.html")

# ------------------ Login ------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        phone = request.form['phone']
        password = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE phone = ?", (phone,))
            user = c.fetchone()
            if not user or user[1] != password:
                return "Invalid credentials"
        session['phone'] = phone
        if phone == ADMIN_PHONE:
            return redirect(url_for('admin_panel'))
        return redirect(url_for('home'))
    return render_template("login.html")

# ------------------ Home Page ------------------
@app.route("/home")
def home():
    if 'phone' not in session:
        return redirect(url_for('login'))
    return render_template("home.html")

# ------------------ Application Form ------------------
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
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO applications 
                        (name, phone, email, dob, gender, country, qualification, score, visa_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
            conn.commit()
        return redirect(url_for('home'))
    return render_template("application.html")

# ------------------ Admin Panel ------------------
@app.route("/admin")
def admin_panel():
    if 'phone' not in session or session['phone'] != ADMIN_PHONE:
        return "Unauthorized"
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM applications")
        data = c.fetchall()
    return render_template("admin_panel.html", applications=data)

# ------------------ Contact Page (GET + POST) ------------------
@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("""INSERT INTO messages (name, email, message) VALUES (?, ?, ?)""", (name, email, message))
            conn.commit()
        return redirect(url_for('contact'))
    return render_template("contact.html")

# ------------------ Logout ------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

# ------------------ Run App ------------------
if __name__ == "__main__":
    app.run(debug=True)
