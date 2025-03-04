import pika
import json
import csv
import os

# Configuración de RabbitMQ (utilizando las mismas credenciales que en la API)
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

# Directorio donde se guardarán los archivos CSV
CSV_DIRECTORY = '/app/data'  # Asegúrate de que este volumen se mapea correctamente

# Crear directorio si no existe
if not os.path.exists(CSV_DIRECTORY):
    os.makedirs(CSV_DIRECTORY)

# Función para establecer la conexión a RabbitMQ
def create_rabbitmq_connection():
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials))
        channel = connection.channel()
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error de conexión a RabbitMQ: {e}")
        return None, None

# Función para escribir los datos en un archivo CSV
def write_to_csv(sensor_type, data):
    file_path = f'{CSV_DIRECTORY}/{sensor_type}_data.csv'  # Formato de la ruta del archivo CSV
    
    # Si el archivo no existe, lo crea y escribe el encabezado
    file_exists = os.path.exists(file_path)
    
    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        
        if not file_exists:
            writer.writeheader()  # Escribir encabezado solo si el archivo es nuevo
        writer.writerow(data)

# Función que será llamada cuando se reciba un mensaje
def callback_temperature(ch, method, properties, body):
    data = json.loads(body)
    print(f"Recibido mensaje en la cola sensor_temperature: {data}")
    write_to_csv('temperature', data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_occupancy(ch, method, properties, body):
    data = json.loads(body)
    print(f"Recibido mensaje en la cola sensor_occupancy: {data}")
    write_to_csv('occupancy', data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_energy(ch, method, properties, body):
    data = json.loads(body)
    print(f"Recibido mensaje en la cola sensor_energy: {data}")
    write_to_csv('energy', data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def callback_security(ch, method, properties, body):
    data = json.loads(body)
    print(f"Recibido mensaje en la cola sensor_security: {data}")
    write_to_csv('security', data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Crear conexión y canal de RabbitMQ
connection, channel = create_rabbitmq_connection()

# Asegúrate de que la conexión se haya realizado correctamente
if not connection or not channel:
    print("No se pudo establecer la conexión con RabbitMQ. El servidor podría estar inalcanzable.")
    exit(1)

# Declarar las colas (en caso de que no existan)
channel.queue_declare(queue='sensor_temperature', durable=True)
channel.queue_declare(queue='sensor_occupancy', durable=True)
channel.queue_declare(queue='sensor_energy', durable=True)
channel.queue_declare(queue='sensor_security', durable=True)

# Configurar los consumidores para cada cola con sus respectivos callbacks
channel.basic_consume(queue='sensor_temperature', on_message_callback=callback_temperature)
channel.basic_consume(queue='sensor_occupancy', on_message_callback=callback_occupancy)
channel.basic_consume(queue='sensor_energy', on_message_callback=callback_energy)
channel.basic_consume(queue='sensor_security', on_message_callback=callback_security)

print("Esperando mensajes. Para salir, presiona Ctrl+C.")
try:
    channel.start_consuming()
except KeyboardInterrupt:
    print("El consumidor se detuvo por el usuario.")
finally:
    if connection and channel:
        try:
            channel.close()
            connection.close()
        except Exception as e:
            print(f"Error al cerrar la conexión a RabbitMQ: {e}")