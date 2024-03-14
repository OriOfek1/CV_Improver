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
    applicant_uuid = uuid.uuid4()
    sql = ''' INSERT INTO applicants(applicant_uuid,contact_info,professional_summary,photo_base64)
              VALUES(?,?,?,?) '''
    applicant_data = (str(applicant_uuid),) + applicant
    cur = conn.cursor()
    cur.execute(sql, applicant_data)
    conn.commit()
    return applicant_uuid

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

def insert_skills(conn, skill):
    sql = ''' INSERT INTO skills(applicant_uuid,skill_name,proficiency_level)
            VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, skill)
    conn.commit()
    return cur.lastrowid

def insert_language(conn, language):
    sql = ''' INSERT INTO skills(applicant_uuid,language,proficiency_level)
                VALUES(?,?,?)'''
    cur = conn.cursor()
    cur.execute(sql, language)
    conn.commit()
    return cur.lastrowid

def get_applicant(conn, uuid):
    cur = conn.cursor()
    cur.execute("SELECT * FROM applicants WHERE applicant_uuid=?", (uuid,))
    return cur.fetchone()

def main():
    pass


