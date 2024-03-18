from celery import Celery
from kombu import serialization

serialization.register_pickle()
serialization.enable_insecure_serializers()


def make_celery(app_name=__name__):
    """
    Makes the Celery backend scheduler and task broker.

    :param app_name: Flask app name
    :return: Celery instance
    """
    backend = "redis://localhost:6379/0"
    broker = backend.replace("0", "1")
    return Celery(
        app_name,
        backend=backend,
        broker=broker,
        task_serializer='pickle',
        result_serializer='pickle',
        accept_content=['pickle', 'application/x-python-serialize']
    )


celery = make_celery()
"Initializes global Celery instance for task assignment."
