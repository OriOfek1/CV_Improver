import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app import app


@pytest.fixture
def test_app() -> FastAPI:
    return app


@pytest.mark.asyncio
async def test_root_endpoint(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "<html>" in response.text  # Adjust according to your index.html content


@pytest.mark.asyncio
async def test_log_message_endpoint(test_app):
    log_data = {"message": "Test log", "level": "info"}
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.post("/log", json=log_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Log received", "level": "info", "log_message": "Test log"}


@pytest.mark.asyncio
async def test_submit_cover_letter_endpoint(test_app):
    # This test requires a file, so it's a bit more complex to setup
    # You might need to adjust this depending on how your endpoint is designed
    pass  # Implement as needed


@pytest.mark.asyncio
async def test_automatic_signup_endpoint(test_app, mocker):
    # Assuming your function `parse_CV` does a lot of work and interacts with files
    # It's a good idea to mock it to return a predictable response
    mocker.patch('CV_parser.main', return_value={"name": "John Doe", "email": "john@example.com"})

    file_content = b'This is a test CV'
    files = {'cv_file': ('test_cv.docx', file_content, 'application/octet-stream')}
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        response = await ac.post("/automatic_signup", files=files)
    assert response.status_code == 200
    assert response.json() == {"message": "Signup successful!",
                               "parsed_data": {"name": "John Doe", "email": "john@example.com"}}


