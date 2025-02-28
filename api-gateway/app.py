from flask import Flask, request, jsonify
import pika
import json

# Configuración de RabbitMQ
RABBITMQ_HOST = 'RABBITMQ_HOST'

# Crear la instancia de Flask
app = Flask(__name__)

# Función para enviar los datos a RabbitMQ
def send_to_rabbitmq(queue: str, data: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=True)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
    )
    connection.close()

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
    app.run(debug=True, host="0.0.0.0", port=5000)
