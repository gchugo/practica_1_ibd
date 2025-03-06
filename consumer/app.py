import pika
import os
import csv
import json
import logging
import threading
import time

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuración de RabbitMQ (usando credenciales de las variables de entorno)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'myuser')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'mypassword')

time.sleep(20)

# Función para manejar los mensajes de cada sensor y guardarlos en un CSV
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)  # Los datos pueden ser un diccionario o una lista de diccionarios
        sensor = method.routing_key
        logger.info(f"Recibidos datos del sensor {sensor}: {data}")
        
        # Verificar si los datos son una lista
        if isinstance(data, list):
            # Si es una lista, recorremos cada diccionario
            for item in data:
                if isinstance(item, dict):
                    file_path = f'/app/data/{sensor}.csv'
                    with open(file_path, mode='a', newline='') as file:
                        writer = csv.DictWriter(file, fieldnames=item.keys())
                        if file.tell() == 0:  # Si el archivo está vacío, escribir los encabezados
                            writer.writeheader()
                        writer.writerow(item)
        elif isinstance(data, dict):
            # Si los datos son un solo diccionario
            file_path = f'/app/data/{sensor}.csv'
            with open(file_path, mode='a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=data.keys())
                if file.tell() == 0:  # Si el archivo está vacío, escribir los encabezados
                    writer.writeheader()
                writer.writerow(data)
        else:
            logger.error(f"Datos del sensor {sensor} no están en el formato esperado (diccionario o lista).")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Confirmar el mensaje
    except Exception as e:
        logger.error(f"Error al procesar el mensaje: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag)  # Rechazar el mensaje si hay error

# Establecer la conexión a RabbitMQ y comenzar a consumir
def consume(sensor: str):
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()

        # Declarar la cola para el sensor específico
        channel.queue_declare(queue=sensor, durable=True)

        logger.info(f"Esperando mensajes del sensor {sensor}...")

        # Iniciar el consumo de mensajes
        channel.basic_consume(queue=sensor, on_message_callback=callback)

        # Comenzar a consumir de la cola
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Error de conexión a RabbitMQ para el sensor {sensor}: {e}")
    except KeyboardInterrupt:
        logger.info("Consumo detenido por el usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")

# Función principal que ejecuta el consumidor para cada sensor en un hilo
if __name__ == '__main__':
    sensors = ['sensor_temperature', 'sensor_occupancy', 'sensor_energy', 'sensor_security']
    
    # Crear y arrancar un hilo para cada sensor
    threads = []
    for sensor in sensors:
        thread = threading.Thread(target=consume, args=(sensor,))
        thread.start()
        threads.append(thread)
    
    # Esperar a que todos los hilos terminen (aunque en este caso, el consumo es indefinido)
    for thread in threads:
        thread.join()