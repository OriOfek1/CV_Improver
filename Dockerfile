FROM python:3.8

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV PORT=80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]
