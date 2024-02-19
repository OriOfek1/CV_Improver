import sqlite3
from sqlite3 import Error
import json
import uuid
import create_database

def create_connection(db_file="database.db"):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database version {sqlite3.version}")
    except Error as e:
        print(e)
    return conn

def insert_applicant(conn, applicant):
    sql = ''' INSERT INTO applicants(uuid,contact_info,professional_summary,photo_base64)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, applicant)
    conn.commit()
    return cur.lastrowid

def insert_education(conn, education):
    sql = ''' INSERT INTO education(applicant_uuid,school_name,level,start_date,end_date,gpa,field_of_study,achievements,extra_notes)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, education)
    conn.commit()
    return cur.lastrowid

def insert_work_experience(conn, work_experience):
    sql = ''' INSERT INTO work_experience(applicant_uuid,title,company_name,achievements,extra_notes)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, work_experience)
    conn.commit()
    return cur.lastrowid

def get_applicant(conn, uuid):
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicants WHERE uuid=?", (uuid,))
    return cur.fetchone()

def main():
    database = "database.db"
    conn = create_connection(database)

    if conn is not None:
        applicant_uuid = str(uuid.uuid4())
        applicant_data = (applicant_uuid, json.dumps({"email": "john.doe@example.com", "phone": "123-456-7890"}), "An experienced software developer...", "PHOTO_BASE64_PLACEHOLDER")
        insert_applicant(conn, applicant_data)

        education_data = (applicant_uuid, "Example University", "Bachelor", "2010-08-01", "2014-05-30", 3.5, "Computer Science", "Dean's List", "Participated in a study abroad program")
        insert_education(conn, education_data)

        work_experience_data = (applicant_uuid, "Senior Developer", "Example Corp", json.dumps(["Led a team of 5 developers", "Increased system efficiency by 20%"]), "Worked on a variety of projects...")
        insert_work_experience(conn, work_experience_data)

        print("Data inserted successfully. Applicant UUID:", applicant_uuid)
    else:
        print("Error! Cannot create the database connection.")


