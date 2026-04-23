import pika
import time
import logging
import json
from database.database import engine 
from sqlmodel import Session
from models.ml_task import MLTask, TaskStatus
import uuid
from database.config import get_settings
from llm import do_task

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

logger = logging.getLogger(__name__)

settings = get_settings()

worker_id = str(uuid.uuid4())[:8]
logger.info(f"Worker ID: {worker_id}")

connection_params = pika.ConnectionParameters(
    host=settings.RABBITMQ_HOST, 
    port=settings.RABBITMQ_PORT,
    virtual_host='/',
    credentials=pika.PlainCredentials(
        username=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASS
    ),
    heartbeat=0,
    blocked_connection_timeout=None
)

connection = pika.BlockingConnection(connection_params)
channel = connection.channel()
queue_name = settings.RABBITMQ_QUEUE_NAME
channel.queue_declare(queue=queue_name)  # Создание очереди (если не существует)

# Функция, которая будет вызвана при получении сообщения
def callback(ch, method, properties, body):
    task_id = None
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
                
        image_url = features.get("x1")
        manual_text = features.get("x2")

        prediction = do_task(
            image_url=image_url,
            manual_text=manual_text
        )

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
        logger.exception(f"Ошибка при обработке сообщения: {str(e)}")

        if task_id is not None:
            with Session(engine) as session:
                task = session.get(MLTask, task_id)
                if task:
                    task.status = TaskStatus.FAILED
                    task.result_text = str(e)
                    session.add(task)
                    session.commit()

        try:
            if ch.is_open:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ack_error:
            logger.error(f"Не удалось подтвердить сообщение после ошибки: {ack_error}")

# Подписка на очередь и установка обработчика сообщений
channel.basic_consume(
    queue=queue_name,
    on_message_callback=callback,
    auto_ack=False  # Автоматическое подтверждение обработки сообщений
)

logger.info('Waiting for messages. To exit, press Ctrl+C')
channel.start_consuming()

