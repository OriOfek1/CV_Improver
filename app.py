import base64

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

@app.route('/manual_signup')
def manual_signup():
    return render_template('manual_signup.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    try:
        contact_info = request.form.to_dict(flat=False)
        print(contact_info)
        professional_summary = request.form['professional_summary']
        photo = request.files['photo'] if 'photo' in request.files else None

        # Handle photo file
        photo_base64 = ""
        if photo:
            photo_base64 = base64.b64encode(photo.read()).decode('utf-8')

        conn = update_database.create_connection("database.db")
        applicant_uuid = update_database.insert_applicant(conn, (
            contact_info['email'][0],
            professional_summary,
            photo_base64
        ))
        print("?")

        return jsonify(
            {"success": True, "message": "Data submitted successfully", "applicant_uuid": applicant_uuid})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


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
