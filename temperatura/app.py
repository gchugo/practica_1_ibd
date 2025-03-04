import random
import time
import json
import requests
import os
import logging

time.sleep(10)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Función para generar datos aleatorios de un sensor de temperatura/humedad
def generate_temp_humidity_data(sensor_id):
    data = {
        "sensor_id": sensor_id,
        "temperature_C": round(random.uniform(18.0, 30.0), 2),  # Temperatura en grados Celsius
        "humidity_%": round(random.uniform(30.0, 70.0), 2),     # Humedad en porcentaje
        "air_quality_index": random.choice(["low", "medium", "high"])  # Índice de calidad de aire
    }
    return data

# Simula los datos de un sensor de temperatura/humedad y los envía a la API
def simulate_temp_humidity_sensor(api_url):
    sensor_id = os.getenv('HOSTNAME', 'default_sensor')  # Obtener el nombre del contenedor desde el entorno
    while True:
        data = generate_temp_humidity_data(sensor_id)
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                logger.info(f"Data sent successfully for sensor {sensor_id}: {data}")
            else:
                logger.error(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {e}")
        time.sleep(30)  # Espera 30 segundos antes de generar los próximos datos

if __name__ == "__main__":
    api_url = "http://api-gateway:5001/api/temperature"  # Usar el nombre del servicio 'api-gateway'
    simulate_temp_humidity_sensor(api_url=api_url)