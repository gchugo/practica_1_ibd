import random
import time
import json

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

# Simula los datos de un sensor de ocupación
def simulate_occupancy_sensor(sensor_id):
    while True:
        data = generate_occupancy_data(sensor_id)
        print(json.dumps(data))  # Imprime los datos en formato JSON
        time.sleep(60)  # Espera 1 minuto antes de generar los próximos datos

if __name__ == "__main__":
    simulate_occupancy_sensor(sensor_id=1)