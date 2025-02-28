import random
import time
import json

# Función para generar datos aleatorios de un medidor de consumo de energía
def generate_power_data(sensor_id):
    data = {
        "sensor_id": sensor_id,
        "power_consumption_kWh": round(random.uniform(0.1, 10.0), 2),  # Consumo de energía en kWh
        "voltage_V": round(random.uniform(220.0, 240.0), 2),           # Voltaje en V
        "current_A": round(random.uniform(0.1, 20.0), 2),               # Corriente en A
        "power_factor": round(random.uniform(0.7, 1.0), 2)              # Factor de potencia (0-1)
    }
    return data

# Simula los datos de un medidor de consumo de energía
def simulate_single_power_meter(sensor_id):
    while True:
        data = generate_power_data(sensor_id)
        print(json.dumps(data))  # Imprime los datos en formato JSON
        time.sleep(5)  # Espera 5 segundos antes de generar los próximos datos

if __name__ == "__main__":
    simulate_single_power_meter(sensor_id=1)