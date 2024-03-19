import os

from flask import Flask
from flask_apscheduler import APScheduler
from flask_dropzone import Dropzone
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from app.celery_utils import init_celery
from config import Config

PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
"Current project package name"
csrf = CSRFProtect()
"CSRF tokenization protection all over the app"
dropzone = Dropzone()
"File upload manager"
scheduler = APScheduler()
"Task scheduler"
sql_db = SQLAlchemy()
"SQL database"


def create_app(app_name=PKG_NAME, **kwargs):
    """
    Creates the Flask app and initializes:

    - CSRF

    - Dropzone

    - APScheduler

    - SQLAlchemy DB

    - Emotion Analysis Task Manager

    :param app_name: name of the flask app
    :param kwargs: keyword arguments for Flask initialization
    :return: Flask application object
    """

    app = Flask(app_name)
    app.config.from_object(Config)
    csrf.init_app(app)
    dropzone.init_app(app)
    scheduler.init_app(app)
    sql_db.init_app(app)
    emotion_analysis_task_manager.init_app(app)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    from app.all import bp
    app.register_blueprint(bp)

    with app.app_context():
        sql_db.create_all()
        scheduler.add_job(
            id="update_ea_tasks",
            trigger="interval",
            func=emotion_analysis_task_manager.update,
            seconds=25
        )
        scheduler.start()

    return app


from app.ea_tasks import EmotionAnalysisTaskManager
emotion_analysis_task_manager = EmotionAnalysisTaskManager()
"Emotion Analysis Task Manager"
