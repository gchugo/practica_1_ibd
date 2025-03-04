from flask import Flask, request, jsonify
import pika
import json
import os
import time
import logging

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logging.getLogger('pika').setLevel(logging.WARNING)  # Solo los warnings y errores de pika se verán
logger = logging.getLogger(__name__)

time.sleep(10)  # Espera para que RabbitMQ esté completamente listo

# Configuración de RabbitMQ (usando credenciales de las variables de entorno)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')  # Valor por defecto 'guest'
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')  # Valor por defecto 'guest'

# Crear la instancia de Flask
app = Flask(__name__)

# Función para establecer la conexión a RabbitMQ
def create_rabbitmq_connection():
    try:
        logger.info(f"Intentando conectar a RabbitMQ en {RABBITMQ_HOST}...")
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        # Asegurarse de que las colas estén declaradas
        channel.queue_declare(queue='sensor_temperature', durable=True)
        channel.queue_declare(queue='sensor_occupancy', durable=True)
        channel.queue_declare(queue='sensor_energy', durable=True)
        channel.queue_declare(queue='sensor_security', durable=True)
        logger.info("Conexión a RabbitMQ exitosa.")
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error de conexión a RabbitMQ: {e}")
        return None, None

# Crear conexión y canal de RabbitMQ fuera de la función
connection, channel = create_rabbitmq_connection()

# Asegurarse de que la conexión se haya realizado correctamente
if not connection or not channel:
    logger.error("No se pudo establecer la conexión con RabbitMQ. El servidor podría estar inalcanzable.")
    exit(1)

# Función para enviar los datos a RabbitMQ
def send_to_rabbitmq(queue: str, data: dict):
    try:
        channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)  # Hacer que el mensaje sea persistente
        )
        logger.info(f"Datos enviados a la cola {queue} correctamente.")
    except Exception as e:
        logger.error(f"Error al enviar datos a RabbitMQ: {e}")

# Endpoints para recibir los datos de los sensores y enviar a RabbitMQ
@app.route("/api/temperature", methods=["POST"])
def receive_temperature_data():
    try:
        data = request.json
        logger.info(f"Datos de temperatura recibidos: {data}")
        send_to_rabbitmq('sensor_temperature', data)
        return jsonify({"message": "Temperature data received"}), 200
    except Exception as e:
        logger.error(f"Error en el endpoint /api/temperature: {e}")
        return jsonify({"error": "Error processing temperature data"}), 500

@app.route("/api/occupancy", methods=["POST"])
def receive_occupancy_data():
    try:
        data = request.json
        logger.info(f"Datos de ocupación recibidos: {data}")
        send_to_rabbitmq('sensor_occupancy', data)
        return jsonify({"message": "Occupancy data received"}), 200
    except Exception as e:
        logger.error(f"Error en el endpoint /api/occupancy: {e}")
        return jsonify({"error": "Error processing occupancy data"}), 500

@app.route("/api/energy", methods=["POST"])
def receive_energy_data():
    try:
        data = request.json
        logger.info(f"Datos de energía recibidos: {data}")
        send_to_rabbitmq('sensor_energy', data)
        return jsonify({"message": "Energy data received"}), 200
    except Exception as e:
        logger.error(f"Error en el endpoint /api/energy: {e}")
        return jsonify({"error": "Error processing energy data"}), 500

@app.route("/api/security", methods=["POST"])
def receive_security_data():
    try:
        data = request.json
        logger.info(f"Datos de seguridad recibidos: {data}")
        send_to_rabbitmq('sensor_security', data)
        return jsonify({"message": "Security data received"}), 200
    except Exception as e:
        logger.error(f"Error en el endpoint /api/security: {e}")
        return jsonify({"error": "Error processing security data"}), 500

if __name__ == "__main__":
    try:
        logger.info("Iniciando el servidor Flask...")
        app.run(debug=False, host="0.0.0.0", port=5001)  # Desactivamos el debug
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario.")
    finally:
        # Cerrar la conexión y el canal de RabbitMQ
        if connection and channel:
            try:
                channel.close()
                connection.close()
                logger.info("Conexión con RabbitMQ cerrada.")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión a RabbitMQ: {e}")