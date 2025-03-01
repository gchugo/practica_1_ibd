import random
import time
import json
import requests

# URL de la API a la que se enviarán los datos
API_URL = "http://localhost:5000/sensor-data"  # Cambia esta URL a la de tu API

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
def simulate_occupancy_sensor(sensor_id):
    while True:
        data = generate_occupancy_data(sensor_id)
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Datos enviados correctamente: {json.dumps(data)}")
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
        time.sleep(60)  # Espera 1 minuto antes de generar los próximos datos

if __name__ == "__main__":
    simulate_occupancy_sensor(sensor_id=1)