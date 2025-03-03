from flask import Flask, request, jsonify
import pika
import json
import os
import time

time.sleep(5)  # Espera para que RabbitMQ esté completamente listo

# Configuración de RabbitMQ (usando credenciales de las variables de entorno)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')  # Valor por defecto 'guest'
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')  # Valor por defecto 'guest'

# Crear la instancia de Flask
app = Flask(__name__)

# Establecer la conexión a RabbitMQ fuera de la función
credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
channel = connection.channel()

# Asegurarse de que haya solo una cola común para todos los sensores
channel.queue_declare(queue='sensor_data', durable=True)

# Función para enviar los datos a RabbitMQ
def send_to_rabbitmq(sensor_type: str, data: dict):
    # Añadir el tipo de sensor a los datos
    data['sensor_type'] = sensor_type
    channel.basic_publish(
        exchange='',
        routing_key='sensor_data',  # Usamos la única cola
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )

# Endpoints para recibir los datos de los sensores y enviar a RabbitMQ
@app.route("/api/temperature", methods=["POST"])
def receive_temperature_data():
    data = request.json
    send_to_rabbitmq('sensor_temperature', data)
    return jsonify({"message": "Temperature data received"}), 200

@app.route("/api/occupancy", methods=["POST"])
def receive_occupancy_data():
    data = request.json
    send_to_rabbitmq('sensor_occupancy', data)
    return jsonify({"message": "Occupancy data received"}), 200

@app.route("/api/energy", methods=["POST"])
def receive_energy_data():
    data = request.json
    send_to_rabbitmq('sensor_energy', data)
    return jsonify({"message": "Energy data received"}), 200

@app.route("/api/security", methods=["POST"])
def receive_security_data():
    data = request.json
    send_to_rabbitmq('sensor_security', data)
    return jsonify({"message": "Security data received"}), 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)