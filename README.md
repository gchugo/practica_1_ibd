# 📡 Smart Building Monitoring System

Este proyecto consiste en una infraestructura de monitoreo de un edificio inteligente a través de sensores conectados que recogen y procesan datos en tiempo real. Los datos son enviados a una API y almacenados en CSVs usando contenedores Docker. Esta infraestructura incluye la integración de **Flask**, **RabbitMQ**, **Pika**, y **Docker**.

## Sensores integrados

El sistema monitorea el edificio usando los siguientes tipos de sensores:

### 1. 🌡️ Temperature/Humidity Sensors
- **Datos recogidos**: 
  - Temperatura (°C)
  - Humedad (%)
  - Índice de calidad del aire (bajo, medio, alto)
- **Frecuencia**: cada 30 segundos
- **Volumen**: 4 dispositivos distribuidos por el edificio

### 2. 👥 Occupancy Sensors
- **Datos recogidos**:
  - Ocupación (número de personas)
  - Movimiento (booleano)
  - Localización (ID de zona)
  - Tiempo de permanencia (minutos)
- **Frecuencia**: cada 1 minuto
- **Volumen**: 6 dispositivos distribuidos en entradas, pasillos y áreas comunes

### 3. ⚡ Power Consumption Meters
- **Datos recogidos**:
  - Consumo de energía (kWh)
  - Voltaje (V)
  - Corriente (A)
  - Factor de potencia (0-1)
- **Frecuencia**: cada 5 segundos
- **Volumen**: 7 dispositivos (uno por piso y varios en sistemas críticos)

### 4. 📹 Security Cameras
- **Datos recogidos**:
  - Estado (activo/inactivo)
  - Alertas (texto descriptivo del evento: "movimiento detectado", "persona no autorizada", "objeto abandonado")
  - Nivel de alerta (bajo, medio, alto)
- **Frecuencia**: cada 2 minutos para estados y alertas
- **Volumen**: 3 cámaras en puntos estratégicos
## API Overview

La API es responsable de recibir datos de sensores y enviarlos a un sistema de mensajería (RabbitMQ) para su procesamiento asíncrono, asegurando una infraestructura robusta para la gestión de información en tiempo real.

### 🛠️ Endpoints disponibles

La API ofrece varios endpoints para recibir los datos de diferentes sensores del sistema:

1. 🌡️ /api/temperature (POST)
	- Descripción: Recibe datos relacionados con la temperatura ambiental, humedad relativa y calidad del aire.
	- Uso: Los datos se envían a la cola sensor_temperature en RabbitMQ para su procesamiento posterior.

2. 👥 /api/occupancy (POST)
	- Descripción: Recibe información sobre la ocupación de espacios, como detección de movimiento y número de personas en una sala.
	- Uso: Los datos son encolados en sensor_occupancy en RabbitMQ para su análisis y acciones futuras.

3. ⚡ /api/energy (POST)
   	- Descripción: Recibe datos sobre el consumo de energía, como el consumo en kWh, voltaje, corriente y otros parámetros eléctricos.
	- Uso: Los datos se envían a la cola sensor_energy en RabbitMQ, facilitando su monitoreo y análisis energético. Para esta cola, los datos se envían en lotes (batch) a RabbitMQ, optimizando así la carga de mensajes y mejorando el rendimiento del sistema debido a que recibe muchos mensajes y la cola se puede saturar.

4. 🔒 /api/security (POST)
	- Descripción: Recibe datos de seguridad, como el estado de las cámaras de vigilancia o alertas de movimiento en áreas críticas.
	- Uso: La información es enviada a la cola sensor_security en RabbitMQ para permitir una respuesta rápida ante eventos de seguridad.

⸻

### Funcionamiento General de la API
1.	La API recibe datos en formato JSON desde los sensores conectados.
2.	Cada tipo de sensor tiene un endpoint dedicado para recibir sus datos específicos.
3.	Los datos se envían a RabbitMQ, donde se encolan y se procesan asíncronamente.
4.	Gracias a RabbitMQ, los datos se mantienen persistentes, asegurando que no se pierdan incluso si los consumidores no están disponibles inmediatamente.

### Conexiones y Consumo de Datos con RabbitMQ
• La API maneja conexiones a RabbitMQ de forma eficiente mediante la biblioteca pika, asegurando que los datos se envíen y reciban sin pérdida de mensajes, incluso si se presentan interrupciones en la conexión.

• Conexiones establecidas: La API mantiene una conexión activa con RabbitMQ para cada tipo de sensor, utilizando credenciales de entorno definidas para asegurar la comunicación.

• Manejo de reconexiones: En caso de que se cierre una conexión o canal, la API se encarga de reconectar automáticamente, manteniendo la disponibilidad del sistema.

• Cada uno de los sensores tiene su propia conexión, canal y cola de forma que, en el caso de que se produzca algún bloqueo del canal, alguna desconexión por parte del consumidor o se sature la cola, el resto de comunicaciones entre sensores y consumidores seguirá funcionando mientras se trata de recuperar la conexión del elemento caido.

## Tecnologías utilizadas

El sistema utiliza las siguientes tecnologías para su infraestructura:

- **API y Sensores**: [Flask](https://flask.palletsprojects.com/)
- **Mensajería y Queues**: [RabbitMQ](https://www.rabbitmq.com/) + [Pika](https://pika.readthedocs.io/en/stable/)
- **Contenerización y Orquestación**: [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/)

## Montar la infraestructura

Puedes montar la infraestructura utilizando Docker Compose. Los contenedores necesarios, como la API, los sensores, y el consumidor, están disponibles en Docker Hub.

### Despliegue:
   ```bash
   git clone git@github.com:gchugo/practica_1_ibd.git
   cd practica_1_ibd
   docker compose up
   ```
### Acceso a los datos:
   ```bash
   curl -X GET http://localhost:5001/api/get_csv/sensor_temperature.csv --output sensor_temperature.csv
   curl -X GET http://localhost:5001/api/get_csv/sensor_occupancy.csv --output sensor_occupancy.csv
   curl -X GET http://localhost:5001/api/get_csv/sensor_energy.csv --output sensor_energy.csv
   curl -X GET http://localhost:5001/api/get_csv/sensor_security.csv --output sensor_security.csv
   ```
