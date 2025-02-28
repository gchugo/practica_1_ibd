import random
import time
import json

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

# Simula los datos de una cámara de seguridad
def simulate_security_camera(camera_id):
    while True:
        data = generate_camera_data(camera_id)
        print(json.dumps(data))  # Imprime los datos en formato JSON
        time.sleep(120)  # Espera 2 minutos (120 segundos) antes de generar los próximos datos

if __name__ == "__main__":
    simulate_security_camera(camera_id=1)