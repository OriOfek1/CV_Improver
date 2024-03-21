import requests
import json
from pypdf import PdfReader
from openai import OpenAI
import ast

url = 'http://localhost:8080'
FORMAT = {
    "applicant_data": "{\"full_name\": \"[Full Name]\", \"email\": \"[Email Address]\", \"phone\": \"[Phone Number]\", \"professional_summary\": \"[Brief Professional Summary]\", \"title\": \"[Current Title or Position]\"}",
    "education": "[{\"school_name\": \"[Institution Name]\", \"level\": \"[Degree Level]\", \"start_date\": \"[Start Date]\", \"end_date\": \"[End Date]\", \"gpa\": [GPA], \"field_of_study\": \"[Field of Study]\", \"achievements\": \"[Key Achievements]\", \"extra_notes\": \"[Additional Notes]\"}]",
    "projects": "[{\"project_name\": \"[Project Name]\", \"project_description\": \"[Project Description]\", \"extra_notes\": \"[Technologies Used and Other Notes]\"}]",
    "work_experience": "[{\"title\": \"[Job Title]\", \"company_name\": \"[Company Name]\", \"achievements\": \"[Key Achievements in the Role]\", \"extra_notes\": \"[Additional Notes]\"}]",
    "skills": "[{\"name\": \"[Skill Name]\", \"level\": \"[Skill Level]\"}]",
    "languages": "[{\"name\": \"[Language]\", \"level\": \"[Proficiency Level]\"}]",
    "volunteering": "[{\"organization\": \"[Organization Name]\", \"role\": \"[Role]\", \"details\": \"[Details of the Volunteer Work]\"}]"
}

def extract_text_from_cv(cv):
    reader = PdfReader(cv)
    page = reader.pages[0]
    text = page.extract_text()
    return text

def output_format(text):
    client = None
    try:
        client = OpenAI(api_key='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')
    except Exception as e:
        print(str(e))
    prompt = (f"""You are a professional recruiter, perfect for helping candidates get their dream jobs.
                     Given the following text parsed from an applicant's CV, rewrite it in a format suitable for
                     adding it to our database. It is very important that you won't add data that is not real
                     about the candidate.
                     This is the applicant's data: {text}
                     Output only the python dictionary, without any explanation or details, do it according to this format: {FORMAT}
                     Notice that besides "applicant_data", all items in the json are lists because they can have multiple values.
                     Make sure to avoid using ' in the text, as it'll break the json parsing.""")
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="gpt-3.5-turbo"
    )
    applicant_data = chat_completion.choices[0].message.content
    print("applicant_data:")
    print(applicant_data)

    applicant_data = ast.literal_eval(applicant_data)

    for key in applicant_data:
        if not isinstance(applicant_data[key], str) or (applicant_data[key][0] not in ['{', '[']):
            applicant_data[key] = json.dumps(applicant_data[key])
    return applicant_data


def api_call(applicant_data):
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url + '/submit_form', headers=headers, data=json.dumps(applicant_data))
    if response.status_code == 200:
        print("Submission successful.")
        print(response.json())
    else:
        print(f"Submission failed with status code: {response.status_code}")
        print(response.text)

def main(cv):
    text = extract_text_from_cv(cv)
    applicant_data = output_format(text)
    api_call(applicant_data)

if __name__ == "__main__":
    main('static/CV/Sharon Shechter CV.pdf')