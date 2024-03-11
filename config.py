import os


class Config:
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
