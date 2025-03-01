import pika
import csv
import json

# Configuración de RabbitMQ
RABBITMQ_HOST = 'RABBITMQ_HOST'

# Diccionario para mantener referencias a los archivos CSV abiertos
csv_files = {}
csv_writers = {}

# Función para abrir el archivo CSV de un sensor si no está abierto
def open_csv(sensor_type):
    if sensor_type not in csv_files:
        # Abrir o crear un nuevo archivo CSV para el sensor
        csv_file = open(f'{sensor_type}_data.csv', mode='a', newline='')
        csv_writer = csv.writer(csv_file)
        
        # Escribir el encabezado si el archivo está vacío
        if csv_file.tell() == 0:
            csv_writer.writerow(['data'])  # Cambia esto según los datos que recibas
        
        # Guardar las referencias al archivo y al writer
        csv_files[sensor_type] = csv_file
        csv_writers[sensor_type] = csv_writer

# Función para consumir mensajes desde RabbitMQ y escribir en CSV
def callback(ch, method, properties, body):
    data = json.loads(body)
    queue_name = method.routing_key  # Nombre de la cola (sensor)

    # Abrir el archivo CSV correspondiente al sensor si no está abierto
    open_csv(queue_name)
    
    print(f"Received data from {queue_name}: {data}")
    
    # Escribir los datos en el archivo CSV del sensor
    csv_writers[queue_name].writerow([json.dumps(data)])  # Almacena los datos como JSON o extrae campos específicos
    
    # Confirmar que el mensaje ha sido procesado
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Configurar conexión a RabbitMQ
def consume_from_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declarar las colas que se van a escuchar
    channel.queue_declare(queue='sensor_temperature', durable=True)
    channel.queue_declare(queue='sensor_occupancy', durable=True)
    channel.queue_declare(queue='sensor_energy', durable=True)
    channel.queue_declare(queue='sensor_security', durable=True)

    # Consumir de cada cola
    channel.basic_consume(queue='sensor_temperature', on_message_callback=callback, auto_ack=False)
    channel.basic_consume(queue='sensor_occupancy', on_message_callback=callback, auto_ack=False)
    channel.basic_consume(queue='sensor_energy', on_message_callback=callback, auto_ack=False)
    channel.basic_consume(queue='sensor_security', on_message_callback=callback, auto_ack=False)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    try:
        consume_from_rabbitmq()
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        # Cerrar todos los archivos CSV abiertos
        for csv_file in csv_files.values():
            csv_file.close()