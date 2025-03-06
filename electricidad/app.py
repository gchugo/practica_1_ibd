import random
import time
import json
import requests
import os
import logging

time.sleep(40)

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Función para generar datos aleatorios de un medidor de consumo de energía
def generate_power_data(sensor_id):
    data = {
        "sensor_type": "power_meter",  # Tipo de sensor
        "sensor_id": sensor_id,  # Usar el nombre del contenedor como ID del sensor
        "power_consumption_kWh": round(random.uniform(0.1, 10.0), 2),  # Consumo de energía en kWh
        "voltage_V": round(random.uniform(220.0, 240.0), 2),           # Voltaje en V
        "current_A": round(random.uniform(0.1, 20.0), 2),               # Corriente en A
        "power_factor": round(random.uniform(0.7, 1.0), 2)              # Factor de potencia (0-1)
    }
    return data

# Simula los datos de un medidor de consumo de energía y los envía a la API
def simulate_single_power_meter(api_url):
    # Obtener el nombre del contenedor como sensor_id
    sensor_id = os.getenv('HOSTNAME', 'default_sensor')
    while True:
        data = generate_power_data(sensor_id)
        try:
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                logger.info(f"Data sent successfully for sensor {sensor_id}: {data}")
            else:
                logger.warning(f"Failed to send data for sensor {sensor_id}. Status code: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error sending data for sensor {sensor_id}: {str(e)}")
        
        time.sleep(5)  # Espera 5 segundos antes de generar los próximos datos

if __name__ == "__main__":
    # Dirección de la API
    api_url = "http://api-gateway:5001/api/energy"  # Usar el nombre del servicio 'api-gateway'
    simulate_single_power_meter(api_url=api_url)