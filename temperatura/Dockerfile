# Dockerfile para el sensor de temperatura
FROM python:3.9-slim

WORKDIR /app
COPY app.py /app
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD ["python", "app.py"]