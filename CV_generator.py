from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
import sqlite3
from docx import Document
import re


def create_CV(user_id, job_description, template_path):
    profile_dict = create_user_profile(user_id)
    print("user id" + user_id)
    print("job_description:" + job_description)
    profile_dict = {'Full name': 'Adi Algazi','About me place holder':'i am adi', 'Exp place holder': 'developer', 'email place holder': 'adi@gmail.com'}
    print(profile_dict)
    # Now template_path is passed as a parameter
    update_word_document_with_user_info(template_path, profile_dict)
    # Return the path of the updated document for further use
    return template_path.replace('.docx', '_updated.docx')


def create_user_profile(user_id):

    # Connect to the SQLite databases
    conn_applicants = sqlite3.connect('database.db')

    # Create a cursor object using the cursor() method
    cursor_applicants = conn_applicants.cursor()

    # Query the applicants database for the user's information
    cursor_applicants.execute('''SELECT contact_info, Professional_summary 
                                 FROM applicants 
                                 WHERE applicant_uuid = ?''', (user_id,))
    applicant_info = cursor_applicants.fetchone()

    # Query the work_experience database for the user's experiences
    cursor_applicants.execute('''SELECT title, company_name, achievements 
                                       FROM work_experience 
                                       WHERE applicant_uuid = ?''', (user_id,))
    experiences = cursor_applicants.fetchall()

    # Building the profile dictionary
    profile = {
        "full name": user_id,
        "About me place holder": applicant_info[1] if applicant_info else "",
        "Experience place holder": "\n".join([f"{exp[0]} at {exp[1]}. {exp[2]}" for exp in experiences]) if experiences else "",
        "Email place holder": applicant_info[0] if applicant_info else ""
    }

    # Close the database connection
    conn_applicants.close()

    return profile


def update_word_document_with_user_info(doc_path, user_info):
    doc = Document(doc_path)

    # Update paragraphs in the main document body
    for paragraph in doc.paragraphs:
        update_paragraph(paragraph, user_info)

    # Update paragraphs in tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    update_paragraph(paragraph, user_info)

    new_doc_path = doc_path.replace('.docx', '_updated.docx')
    doc.save(new_doc_path)
    print(f"Document saved as '{new_doc_path}'.")

def update_paragraph(paragraph, user_info):
    """Check if any key in user_info is in the paragraph, and if so, replace it while preserving formatting."""
    for key, value in user_info.items():
        # Iterate through each run in the paragraph
        for run in paragraph.runs:
            if key.lower() in run.text.lower():
                # Replace key with value in text while preserving formatting
                run.text = run.text.lower().replace(key.lower(), value)
                print("Updated paragraph with key:", key)