# Dockerfile para el Consumer
FROM python:3.9-slim

WORKDIR /consumer

# Copiar los archivos del consumer
COPY requirements.txt requirements.txt
COPY . .

# Instalar las dependencias del consumer
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar el consumer
CMD ["python", "app.py"]