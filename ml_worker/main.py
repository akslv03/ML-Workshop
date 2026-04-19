import pika
import time
import logging
import json
from database.database import engine 
from sqlmodel import Session
from models.ml_task import MLTask, TaskStatus
import uuid

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

worker_id = str(uuid.uuid4())[:8]
logger.info(f"Worker ID: {worker_id}")

connection_params = pika.ConnectionParameters(
    host='rabbitmq', 
    port=5672,
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username='guest',
        password='guest'
    ),
    heartbeat=30,
    blocked_connection_timeout=2
)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = 'ml_task_queue'
channel.queue_declare(queue=queue_name)  # Создание очереди (если не существует)

# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    try:
        message = json.loads(body)
        task_id = message.get("task_id")
        features = message.get("features", {})
        model = message.get("model")
        timestamp = message.get("timestamp")
        
        logger.info(f"Worker_id: {worker_id}. Взята в работу задача №: {task_id}. Модель: {model}. Время: {timestamp}")

        with Session(engine) as session:
            task = session.get(MLTask, task_id)
            if task:
                task.status = TaskStatus.IN_PROGRESS
                session.add(task)
                session.commit()
                
        time.sleep(3)
        prediction = f"Успешная генерация: {features.get('x1')} / {features.get('x2')}"

        logger.info(f"Задача № {task_id} успешно выполнена. Результат: {prediction}")

        with Session(engine) as session:
            task = session.get(MLTask, task_id)
            if task:
                task.status = TaskStatus.COMPLETED
                task.result_text = prediction
                session.add(task)
                session.commit()

        ch.basic_ack(delivery_tag=method.delivery_tag) # Ручное подтверждение обработки сообщения
    
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


# Подписка на очередь и установка обработчика сообщений
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False  # Автоматическое подтверждение обработки сообщений
)

logger.info('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()

