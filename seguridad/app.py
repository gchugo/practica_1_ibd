import random
import time
import json
import requests

# URL de la API a la que se enviarán los datos
API_URL = "http://localhost:5012/api/seguridad"  # Cambia esta URL a la de tu API

# Función para generar datos aleatorios de una cámara de seguridad
def generate_camera_data(camera_id):
    status = random.choice(["active", "inactive"])  # Estado de la cámara (activo/inactivo)
    alert_event = random.choice([
        "motion detected", 
        "unauthorized person", 
        "abandoned object",
        "no event"
    ])  # Tipo de alerta
    alert_level = random.choice(["low", "medium", "high"])  # Nivel de alerta

    # Si no hay evento, no se genera alerta
    if alert_event == "no event":
        alert_level = "none"
    
    data = {
        "camera_id": camera_id,
        "status": status,
        "alert_event": alert_event if status == "active" else "camera inactive",  # Solo alertas si está activa
        "alert_level": alert_level if status == "active" else "none"
    }
    return data

# Simula los datos de una cámara de seguridad y los envía a la API
def simulate_security_camera(camera_id):
    while True:
        data = generate_camera_data(camera_id)
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Datos enviados correctamente: {json.dumps(data)}")
            else:
                print(f"Error al enviar datos: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
        time.sleep(120)  # Espera 2 minutos (120 segundos) antes de generar los próximos datos

if __name__ == "__main__":
    simulate_security_camera(camera_id=1)