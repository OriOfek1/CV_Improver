import sqlite3
import json
from openai import OpenAI
from create_database import create_connection

def fetch_applicant_data(uuid, conn):
    tables = [
        "applicants", "education", "projects", "work_experience",
        "volunteer_work", "languages", "certifications",
        "awards", "skills", "personal_projects"
    ]
    data = {}

    for table in tables:
        data[table] = []
        query = f"SELECT * FROM {table} WHERE applicant_uuid = ?"
        cursor = conn.cursor()
        cursor.execute(query, (uuid,))
        rows = cursor.fetchall()

        # Get column names to use as keys in the dictionaries
        columns = [column[0] for column in cursor.description]

        for row in rows:
            row_data = dict(zip(columns, row))
            data[table].append(row_data)

    return data

def generate_cover_letter(applicant_data, job_data):
    try:
        client = OpenAI(api_key='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')
    except Exception as e:
        print(str(e))
    prompt = (f"""You are a professional recruiter, perfect for helping candidates get their dream jobs.
                 Given the following job description and applicant details, write a cover letter that 
                 highlights the applicants qualities needed for the job (without making anything up).
                 Output only the letter, without any explanation or details.
                 <applicant_data>: {applicant_data}
                 </applicant_data>
                 <job_details>: {job_data}
                 </job_data>""")
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    ai_output = chat_completion.choices[0].message.content
    print(ai_output)

def main():
    database = "database.db"
    uuid = "UUID_PLACEHOLDER"
    conn = create_connection(database)

    if conn is not None:
        applicant_data = fetch_applicant_data(uuid, conn)
        conn.close()

        # Convert the data to JSON format
        applicant_data_json = json.dumps(applicant_data, indent=4)
        print(applicant_data_json)
        job_details = """
        Overview:

CADY is a growing SaaS startup developing a unique product that combines machine learning and electrical engineering.
We are looking for a strong programmer to join a small team and help build and boost the product.


In this role you will:

 Design and build the product infrastructure from its very core.
 Take part in the entire development cycle - design, implement, test, deploy.
 Write sophisticated algorithms for analyzing electrical board drawings.
 

Requirements:

2+ years of programming experience – Must.
Multidisciplinary mindset: able to quickly learn new technologies – Must.
Team player, able to work in a small team – Must.
Experience with Python – Significant advantage.
Experience with React – Advantage.
Knowledge in NLP or image processing – Advantage
B.Sc. in Computer Science/Electrical Engineering or any other technical related fields – Advantage"""
        generate_cover_letter(applicant_data_json, job_details)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    main()
