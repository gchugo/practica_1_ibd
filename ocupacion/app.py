import random
import time
import json
import requests
import os
import logging

time.sleep(40)

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Función para generar datos aleatorios de un sensor de ocupación
def generate_occupancy_data(sensor_id):
    data = {
        "sensor_id": sensor_id,
        "occupancy": random.randint(0, 50),  # Número de personas (0 a 50)
        "movement": random.choice([True, False]),  # Movimiento detectado (True/False)
        "location_zone_id": random.randint(1, 10),  # ID de la zona (de 1 a 10)
        "dwell_time_minutes": round(random.uniform(0.0, 120.0), 2)  # Tiempo de permanencia (en minutos)
    }
    return data

# Simula los datos de un sensor de ocupación y los envía a la API
def simulate_occupancy_sensor(api_url):
    sensor_id = os.getenv('HOSTNAME', 'default_sensor')
    while True:
        data = generate_occupancy_data(sensor_id)
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                logger.info(f"Data sent successfully for sensor {sensor_id}: {data}")
            else:
                logger.error(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {e}")
        time.sleep(60)  # Espera 1 minuto antes de generar los próximos datos

if __name__ == "__main__":
    api_url = "http://api-gateway:5001/api/occupancy"  # Usar el nombre del servicio 'api-gateway'
    simulate_occupancy_sensor(api_url=api_url)