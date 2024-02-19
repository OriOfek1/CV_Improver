from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from sqlite3 import Error
import json
import update_database, create_database

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management and flash messages

DATABASE = 'database.db'

def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_uuid = request.form['uuid']
        conn = sqlite3.connect("database.db")
        if conn:
            applicant = update_database.get_applicant(conn, user_uuid)
            if applicant:
                return redirect(url_for('dashboard', uuid=user_uuid))
            else:
                return "UUID not found. Please try again.", 404
        else:
            return "Database connection error.", 500
    return render_template('login.html')

@app.route('/dashboard/<uuid>')
def dashboard(uuid):
    conn = sqlite3.connect("database.db")
    if conn:
        applicant = update_database.get_applicant(conn, uuid)
        if applicant:
            contact_info = json.loads(applicant[1])
            return render_template('dashboard.html', applicant=applicant, contact_info=contact_info)
        else:
            return "Applicant not found.", 404
    else:
        return "Database connection error.", 500

if __name__ == '__main__':
    app.run(debug=True)
