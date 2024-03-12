import os


class Config:
    FLASK_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

    DROPZONE_MAX_FILE_SIZE = 1 * 1000  # 1 GB
    DROPZONE_DEFAULT_MESSAGE = '<p style="font-size: 1.75rem;">Drop Videos Here<br>Or<br>Click to Upload</p>'
    DROPZONE_ALLOWED_FILE_CUSTOM = True
    DROPZONE_ALLOWED_FILE_TYPE = "video/mkv,video/*"
    DROPZONE_ENABLE_CSRF = True
