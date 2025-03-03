import pika
import csv
import json
import os
import time

time.sleep(10)

# Configuración de RabbitMQ a partir de las variables de entorno
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')  # Valor por defecto 'guest'
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')  # Valor por defecto 'guest'

# Diccionario para mantener referencias a los archivos CSV abiertos
csv_files = {}
csv_writers = {}

# Función para abrir el archivo CSV de un sensor si no está abierto
def open_csv(sensor_type):
    if sensor_type not in csv_files:
        # Ruta donde se guardarán los archivos CSV
        file_path = f'/app/data/{sensor_type}_data.csv'  # Ruta dentro del contenedor, accesible mediante volumen

        # Abrir o crear un nuevo archivo CSV para el sensor
        csv_file = open(file_path, mode='a', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        
        # Escribir el encabezado si el archivo está vacío
        if csv_file.tell() == 0:
            csv_writer.writerow(['data'])  # Escribe la cabecera para los datos recibidos
        
        # Guardar las referencias al archivo y al writer
        csv_files[sensor_type] = csv_file
        csv_writers[sensor_type] = csv_writer

# Función para consumir mensajes desde RabbitMQ y escribir en CSV
def callback(ch, method, properties, body):
    data = json.loads(body)
    sensor_type = data.get('sensor_type', 'unknown')  # Obtener el tipo de sensor desde los datos

    # Abrir el archivo CSV correspondiente al sensor si no está abierto
    open_csv(sensor_type)
    
    print(f"Received data from {sensor_type}: {data}")
    
    # Escribir los datos en el archivo CSV del sensor
    csv_writers[sensor_type].writerow([json.dumps(data)])  # Almacena los datos como JSON o extrae campos específicos

# Configurar conexión a RabbitMQ
def consume_from_rabbitmq():
    try:
        # Conexión utilizando las credenciales configuradas
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                credentials=credentials
            )
        )
        channel = connection.channel()

        # Declarar solo una cola común para todos los sensores
        channel.queue_declare(queue='sensor_data', durable=True)

        # Consumir mensajes de la cola común
        channel.basic_consume(queue='sensor_data', on_message_callback=callback, auto_ack=True)

        print('Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error de conexión a RabbitMQ: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    try:
        consume_from_rabbitmq()
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        # Cerrar todos los archivos CSV abiertos
        for csv_file in csv_files.values():
            csv_file.close()