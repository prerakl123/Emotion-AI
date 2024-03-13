from flask import Flask
import os

from flask_dropzone import Dropzone
from flask_wtf.csrf import CSRFProtect

from app.celery_utils import init_celery
from config import Config

PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]
"Current project package name"
csrf = CSRFProtect()
"CSRF tokenization protection all over the app"
dropzone = Dropzone()
"File upload manager"


def create_app(app_name=PKG_NAME, **kwargs):
    """
    Creates the Flask app and initializes:
    - CSRF
    - Dropzone

    :param app_name: name of the flask app
    :param kwargs: keyword arguments for Flask initialization
    :return: Flask application object
    """
    app = Flask(app_name)
    app.config.from_object(Config)
    csrf.init_app(app)
    dropzone.init_app(app)

    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    from app.all import bp
    app.register_blueprint(bp)

    return app
