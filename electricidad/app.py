import random
import time
import json
import requests

# Función para generar datos aleatorios de un medidor de consumo de energía
def generate_power_data(sensor_id):
    data = {
        "sensor_type": "power_meter",  # Tipo de sensor
        "sensor_id": sensor_id,
        "power_consumption_kWh": round(random.uniform(0.1, 10.0), 2),  # Consumo de energía en kWh
        "voltage_V": round(random.uniform(220.0, 240.0), 2),           # Voltaje en V
        "current_A": round(random.uniform(0.1, 20.0), 2),               # Corriente en A
        "power_factor": round(random.uniform(0.7, 1.0), 2)              # Factor de potencia (0-1)
    }
    return data

# Simula los datos de un medidor de consumo de energía y los envía a la API
def simulate_single_power_meter(sensor_id, api_url):
    while True:
        data = generate_power_data(sensor_id)
        
        try:
            # Enviar los datos a la API
            response = requests.post(api_url, json=data)
            if response.status_code == 200:
                print(f"Data sent successfully for sensor {sensor_id}: {data}")
            else:
                print(f"Failed to send data for sensor {sensor_id}. Status code: {response.status_code}")
        
        except Exception as e:
            print(f"Error sending data: {str(e)}")
        
        time.sleep(5)  # Espera 5 segundos antes de generar los próximos datos

if __name__ == "__main__":
    # Dirección de la API
    api_url = "http://localhost:5000/sensor-data"  # Asegúrate de que tu API esté corriendo en esta URL
    simulate_single_power_meter(sensor_id=1, api_url=api_url)