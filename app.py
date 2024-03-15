from fastapi import FastAPI, Form, File, UploadFile, Request, Response, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
from sqlite3 import Error
import json
import update_database, create_database
import os
from docx import Document
import test
import logging
import base64
import multipart
from typing import List
import jinja2
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # REMEMBER TO FIX
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


DATABASE = 'database.db'

@app.post("/log")
async def log_message(request: Request):
    log_data = await request.json()
    message = log_data.get("message", "")
    level = log_data.get("level", "info").lower()

    logger = logging.getLogger("uvicorn")

    if level == "debug":
        logger.debug(message)
    elif level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)
    else:
        raise HTTPException(status_code=400, detail="Invalid log level")

    return {"message": "Log received", "level": level, "log_message": message}

def get_db_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE)
    except Error as e:
        print(e)
    return conn

@app.get("/", response_class=HTMLResponse)
async def index():
    with open("templates/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/login", response_class=HTMLResponse)
async def get_login():
    with open("templates/login.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/signup", response_class=HTMLResponse)
async def get_signup():
    with open("templates/signup.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/manual_signup", response_class=HTMLResponse)
async def get_manual_signup():
    with open("templates/manual_signup.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/submit-cover-letter/{uuid}")
async def submit_cover_letter(uuid: str, coverLetterText: str = Form(...)):
    cover_letter_content = test.main(coverLetterText)  # Assuming test.main is synchronous

    directory = 'temporary_files'
    if not os.path.exists(directory):
        os.makedirs(directory)

    filename = f"Cover_Letter_for_{uuid}.docx"
    filepath = os.path.join(directory, filename)

    doc = Document()
    doc.add_paragraph(cover_letter_content)
    doc.save(filepath)

    return FileResponse(filepath, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=filename)

@app.get("/generate-cover-letter/{uuid}", response_class=HTMLResponse)
async def generate_cover_letter(uuid: str):
    # You'll need to use a template engine like Jinja2, or manually read and modify the HTML file
    with open("templates/generate_cover_letter.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content.replace("{{uuid}}", uuid))

@app.get("/generate-cv/{uuid}", response_class=HTMLResponse)
async def generate_cv(uuid: str):
    with open("templates/generate_cv.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content.replace("{{uuid}}", uuid))

@app.post("/submit_form")
async def submit_form(
        contact_info: str = Form(...),  # JSON string to handle nested objects
        professional_summary: str = Form(...),
        education: str = Form(...),  # JSON string for education sections
        projects: str = Form(...),  # JSON string for projects
        work_experience: str = Form(...),  # JSON string for work experience
        skills: str = Form(...),  # JSON string for skills
        languages: str = Form(...),  # JSON string for languages
        # photo: Optional[UploadFile] = File(None)  # Optional file upload
):
    # Decode the contact info, education, projects, work experience, skills, and languages from JSON strings
    contact_info_data = json.loads(contact_info)
    education_data = json.loads(education)
    projects_data = json.loads(projects)
    work_experience_data = json.loads(work_experience)
    skills_data = json.loads(skills)
    languages_data = json.loads(languages)
    print(contact_info_data)
    print(education_data)
    print(projects_data)
    print(work_experience_data)
    print(skills_data)
    print(languages_data)

    # Connect to the database
    conn = update_database.create_connection("database.db")

    # Insert main applicant data and retrieve UUID
    applicant_uuid = update_database.insert_applicant(conn, (
        json.dumps(contact_info_data),
        professional_summary
        # photo_base64
    ))

    # Insert data into related tables using the applicant_uuid
    for edu in education_data:
        update_database.insert_education(conn, (applicant_uuid,) + tuple(edu.values()))

    for work in work_experience_data:
        update_database.insert_work_experience(conn, (applicant_uuid,) + tuple(work.values()))

    for project in projects_data:
        update_database.insert_project(conn, (applicant_uuid,) + tuple(project.values()))

    for skill in skills_data:
        update_database.insert_skills(conn, (applicant_uuid,) + tuple(skill.values()))

    for language in languages_data:
        update_database.insert_language(conn, (applicant_uuid,) + tuple(language.values()))

    return {"success": True, "message": "Data submitted successfully", "applicant_uuid": str(applicant_uuid)}

@app.post("/login")
async def post_login(uuid: str = Form(...)):
    return RedirectResponse(url=f"/dashboard/{uuid}", status_code=303)

@app.get("/dashboard/{uuid}", response_class=HTMLResponse)
async def dashboard(request: Request, uuid: str):
    print(uuid)
    conn = get_db_connection()
    if conn:
        applicant = update_database.get_applicant(conn, uuid)
        if applicant:
            print(applicant)
            contact_info = json.loads(applicant[1])
            return templates.TemplateResponse("dashboard.html",
                                              {"request": request,
                                               "contact_info": contact_info,
                                               "applicant": applicant})
        else:
            # Redirect to login with error if the applicant is not found
            return RedirectResponse(url="/login?error=UUID not found", status_code=303)
    else:
        # Redirect to login with error if there's a database connection issue
        return RedirectResponse(url="/login?error=Database connection error", status_code=303)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)