from celery import Celery
import os

BROKER_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672//')
RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

celery_app = Celery('astramech_finance', broker=BROKER_URL, backend=RESULT_BACKEND)
celery_app.conf.task_queues = {
    'finance': {'exchange': 'finance', 'routing_key': 'finance.#'}
}
celery_app.conf.update(task_default_queue='finance', task_serializer='json', accept_content=['json'])
