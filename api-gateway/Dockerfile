# Dockerfile para la API Flask
FROM python:3.9-slim

WORKDIR /app

# Copiar los archivos de la API
COPY requirements.txt .
COPY . .

# Instalar las dependencias de la API
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto en el que se ejecuta Flask
EXPOSE 5001

# Comando para ejecutar Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5001"]