import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))
print(basedir)


class Config:
    """Config class for Flask configurations"""

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    "Secret Key for Flask for CSRF tokens"
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=20)
    "Browser session lifetime"

    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + basedir + '/db/analysis.db'
    "Database URI"

    DROPZONE_MAX_FILE_SIZE = 1 * 1000
    "Default max upload file size: 1 GB"
    DROPZONE_DEFAULT_MESSAGE = '<p style="font-size: 1.75rem;">Drop Videos Here<br>Or<br>Click to Upload</p>'
    "Message displayed when uploading files"
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = "video/mkv,video/*"
    "Allowed file types that can be uploaded"
    DROPZONE_ENABLE_CSRF = True
    "CSRF security tokenization"
