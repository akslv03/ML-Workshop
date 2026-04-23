import pika
import json
from database.config import get_settings

settings = get_settings()

# Параметры подключения
connection_params = pika.ConnectionParameters(
    host=settings.RABBITMQ_HOST,
    port=settings.RABBITMQ_PORT,
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)

def send_task(message:dict):
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    
    # Имя очереди
    queue_name = settings.RABBITMQ_QUEUE_NAME

    # Отправка сообщения
    channel.queue_declare(queue=queue_name)  # Создание очереди (если не существует)
    
    json_message = json.dumps(message)
    
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=json_message
    )

    # Закрытие соединения
    connection.close()