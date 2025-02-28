import random
import time
import json

# Función para generar datos aleatorios de un sensor de temperatura/humedad
def generate_temp_humidity_data(sensor_id):
    data = {
        "sensor_id": sensor_id,
        "temperature_C": round(random.uniform(18.0, 30.0), 2),  # Temperatura en grados Celsius
        "humidity_%": round(random.uniform(30.0, 70.0), 2),     # Humedad en porcentaje
        "air_quality_index": random.choice(["low", "medium", "high"])  # Índice de calidad de aire
    }
    return data

# Simula los datos de un sensor de temperatura/humedad
def simulate_temp_humidity_sensor(sensor_id):
    while True:
        data = generate_temp_humidity_data(sensor_id)
        print(json.dumps(data))  # Imprime los datos en formato JSON
        time.sleep(30)  # Espera 30 segundos antes de generar los próximos datos

if __name__ == "__main__":
    simulate_temp_humidity_sensor(sensor_id=1)