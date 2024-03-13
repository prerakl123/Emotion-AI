from celery import Celery


def make_celery(app_name=__name__):
    """
    Makes the Celery backend scheduler and task broker.

    :param app_name: Flask app name
    :return: Celery instance
    """
    backend = "redis://localhost:6379/0"
    broker = backend.replace("0", "1")
    return Celery(app_name, backend=backend, broker=broker)


celery = make_celery()
"Initializes global Celery instance for task assignment."
