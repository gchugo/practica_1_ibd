import random
import time
import json
import requests

# URL de la API a la que se enviarán los datos
API_URL = "http://localhost:5000/sensor-data"  # Cambia esta URL a la de tu API

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
def simulate_temp_humidity_sensor(sensor_id):
    while True:
        data = generate_temp_humidity_data(sensor_id)
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Datos enviados correctamente: {json.dumps(data)}")
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
        time.sleep(30)  # Espera 30 segundos antes de generar los próximos datos

if __name__ == "__main__":
    simulate_temp_humidity_sensor(sensor_id=1)