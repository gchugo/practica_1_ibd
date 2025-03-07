from flask import Flask, request, jsonify, Response
import pika
import json
import os
import requests
import logging
import time
from collections import deque


# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('pika').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Configuración de RabbitMQ (usando credenciales de las variables de entorno)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'myuser')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'mypassword')

time.sleep(20)

app = Flask(__name__)

# Diccionarios para manejar conexiones y canales
connections = {}
channels = {}

sensors = ['sensor_temperature', 'sensor_occupancy', 'sensor_energy', 'sensor_security']

# Buffer para datos de energía antes de enviarlos en lotes
energy_buffer = deque()
energy_batch_size = 14
last_sent_time_energy = 0
energy_sample_interval = 30

# Función para establecer la conexión a RabbitMQ
def create_rabbitmq_connection(sensor):
    try:
        logger.info(f"Intentando conectar a RabbitMQ en {RABBITMQ_HOST} para {sensor}...")
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        channel.queue_declare(queue=sensor, durable=True)
        logger.info(f"Conexión a RabbitMQ establecida para {sensor}.")
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error al conectar a RabbitMQ para {sensor}: {e}")
        return None, None

# Función para asegurarse de que hay una conexión activa antes de enviar un mensaje
def ensure_rabbitmq_connection(sensor):
    if sensor not in channels or channels[sensor].is_closed:
        logger.warning(f"Canal para {sensor} está cerrado. Intentando reconectar...")
        connections[sensor], channels[sensor] = create_rabbitmq_connection(sensor)
        if not connections[sensor] or not channels[sensor]:
            logger.error(f"No se pudo restablecer la conexión para {sensor}.")
            return False
    return True

# Función para enviar los datos a RabbitMQ
def send_to_rabbitmq(sensor, data):
    if not ensure_rabbitmq_connection(sensor):
        return  # No enviar si la conexión falló

    try:
        channel = channels[sensor]
        channel.basic_publish(
            exchange='',
            routing_key=sensor,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        logger.info(f"Datos enviados a {sensor} correctamente.")
    except Exception as e:
        logger.error(f"Error al enviar datos a {sensor}: {e}")

# Función para recibir datos de un sensor específico
def on_response(ch, method, props, body):
    global response
    response = json.loads(body)

CONSUMER_URL = "http://consumer:5002"

@app.route("/api/get_csv/<filename>", methods=["GET"])
def get_csv_from_consumer(filename):
    try:
        # Hacer una solicitud GET al consumer para obtener el CSV
        response = requests.get(f"{CONSUMER_URL}/csv/{filename}")

        if response.status_code == 200:
            # Retornar el CSV como respuesta
            return Response(response.content, mimetype='text/csv', headers={
                "Content-Disposition": f"attachment;filename={filename}"
            })
        else:
            return jsonify({"error": "No se conecta"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving file: {str(e)}"}), 500

# Función para procesar el buffer de energía y enviarlo en lotes
def process_energy_buffer():
    global last_sent_time_energy
    if len(energy_buffer) >= energy_batch_size or time.time() - last_sent_time_energy >= energy_sample_interval:
        batch_data = list(energy_buffer)
        send_to_rabbitmq('sensor_energy', batch_data)
        energy_buffer.clear()
        last_sent_time_energy = time.time()

# Inicializar conexiones para los sensores
for sensor in sensors:
    connections[sensor], channels[sensor] = create_rabbitmq_connection(sensor)

# Endpoints para los sensores
@app.route("/api/temperature", methods=["POST"])
def receive_temperature_data():
    try:
        data = request.json
        logger.info(f"Recibido: {data}")
        send_to_rabbitmq('sensor_temperature', data)
        return jsonify({"message": "Temperature data received"}), 200
    except Exception as e:
        logger.error(f"Error en /api/temperature: {e}")
        return jsonify({"error": "Error processing temperature data"}), 500

@app.route("/api/occupancy", methods=["POST"])
def receive_occupancy_data():
    try:
        data = request.json
        logger.info(f"Recibido: {data}")
        send_to_rabbitmq('sensor_occupancy', data)
        return jsonify({"message": "Occupancy data received"}), 200
    except Exception as e:
        logger.error(f"Error en /api/occupancy: {e}")
        return jsonify({"error": "Error processing occupancy data"}), 500

@app.route("/api/energy", methods=["POST"])
def receive_energy_data():
    try:
        data = request.json
        logger.info(f"Recibido: {data}")
        energy_buffer.append(data)
        process_energy_buffer()
        return jsonify({"message": "Energy data received"}), 200
    except Exception as e:
        logger.error(f"Error en /api/energy: {e}")
        return jsonify({"error": "Error processing energy data"}), 500

@app.route("/api/security", methods=["POST"])
def receive_security_data():
    try:
        data = request.json
        logger.info(f"Recibido: {data}")
        send_to_rabbitmq('sensor_security', data)
        return jsonify({"message": "Security data received"}), 200
    except Exception as e:
        logger.error(f"Error en /api/security: {e}")
        return jsonify({"error": "Error processing security data"}), 500
    
CONSUMER_URL = os.getenv('CONSUMER_URL', 'http://consumer:5002')

# Ruta en el contenedor de la API donde se almacenan los archivos CSV (si es necesario)
CSV_DIRECTORY = '/app/data'

@app.route('/api/get_csv/<sensor>', methods=['GET'])
def get_csv(sensor):
    try:
        # Hacemos un GET al consumer para obtener el archivo CSV
        response = requests.get(f"{CONSUMER_URL}/csv/{sensor}")

        if response.status_code == 200:
            # Devolver el archivo CSV obtenido del consumer
            return Response(response.content, mimetype='text/csv', headers={
                "Content-Disposition": f"attachment;filename={sensor}"
            })
        else:
            return jsonify({"error": f"CSV file for {sensor} not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error retrieving file: {str(e)}"}), 500


# Cerrar conexiones al salir
def close_connections():
    for sensor, connection in connections.items():
        try:
            connection.close()
            logger.info(f"Conexión cerrada para {sensor}.")
        except Exception as e:
            logger.error(f"Error al cerrar conexión {sensor}: {e}")

if __name__ == "__main__":
    try:
        logger.info("Iniciando Flask...")
        app.run(debug=False, host="0.0.0.0", port=5001)
    except KeyboardInterrupt:
        logger.info("Servidor detenido.")
    finally:
        close_connections()