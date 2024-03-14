from fastapi import FastAPI, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
from sqlite3 import Error
import json
import update_database, create_database
import os
from docx import Document
import test
import base64
import multipart
from typing import List

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")  # For serving static files


DATABASE = 'database.db'

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

@app.post("/signup")
async def signup(username: str = Form(...), password: str = Form(...)):
    conn = get_db_connection()
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
    return RedirectResponse(url="/login", status_code=303)

@app.post("/login")
async def login(uuid: str = Form(...)):
    conn = sqlite3.connect("database.db")
    if conn:
        applicant = update_database.get_applicant(conn, uuid)
        if applicant:
            return RedirectResponse(url=f'/dashboard/{uuid}', status_code=303)
        else:
            raise HTTPException(status_code=404, detail="UUID not found. Please try again.")
    else:
        raise HTTPException(status_code=500, detail="Database connection error.")

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

@app.post("/submit_form")
async def submit_form(
    email: List[str] = Form(...),
    professional_summary: str = Form(...),
    photo: UploadFile = File(None)  # Optional file upload
):
    photo_base64 = ""
    if photo:
        photo_content = await photo.read()
        photo_base64 = base64.b64encode(photo_content).decode('utf-8')

    conn = update_database.create_connection("database.db")
    applicant_uuid = update_database.insert_applicant(conn, (
        email[0],
        professional_summary,
        photo_base64
    ))

    return {"success": True, "message": "Data submitted successfully", "applicant_uuid": applicant_uuid}

@app.get("/dashboard/{uuid}", response_class=HTMLResponse)
async def dashboard(uuid: str):
    conn = sqlite3.connect("database.db")
    if conn:
        applicant = update_database.get_applicant(conn, uuid)
        if applicant:
            contact_info = json.loads(applicant[1])
            # Render your dashboard template here, similar to the generate_cover_letter route
            return HTMLResponse(content=f"Dashboard for UUID: {uuid}")  # Placeholder response
        else:
            raise HTTPException(status_code=404, detail="Applicant not found.")
    else:
        raise HTTPException(status_code=500, detail="Database connection error.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)