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
    return(ai_output)


def main(job_details):
    database = "database.db"
    uuid = "UUID_PLACEHOLDER"
    conn = create_connection(database)

    if conn is not None:
        applicant_data = fetch_applicant_data(uuid, conn)
        conn.close()

        # Convert the data to JSON format
        applicant_data_json = json.dumps(applicant_data, indent=4)
        cover_letter = generate_cover_letter(applicant_data_json, job_details)
        return(cover_letter)
    else:
        print("Error! Cannot create the database connection.")

if __name__ == "__main__":
    main()
