def init_celery(celery, app):
    celery.conf.update(app.config)
    task_base = celery.Task

    class ContextTask(task_base):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
