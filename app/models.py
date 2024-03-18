from app.constants import STATUS
from app.factory import sql_db


class VideoData(sql_db.Model):
    id = sql_db.Column(sql_db.Integer, primary_key=True, autoincrement=True)
    file_hash = sql_db.Column(sql_db.String(25), unique=True)
    frames_processed = sql_db.Column(sql_db.Integer, default=0)
    total_frames = sql_db.Column(sql_db.Integer, default=0)
    original_filename = sql_db.Column(sql_db.String(255))
    status = sql_db.Column(sql_db.String(15), default=False)

    def __repr__(self):
        return f'<VideoData id="{self.id}" hash="{self.file_hash}" filename="{self.original_filename}"'


def get_status_by_file_hash(file_hash: str):
    result = VideoData.query.filter_by(file_hash=file_hash).first()
    print(result)
    return result


def get_file_by_status(
        app,
        status: STATUS,
        m: int = 0,
        n: int = 10
):
    """
    Gets all the records from the VideoData model between `m` to `n` indexes
    :param app: Flask app for context
    :param status: status type from ["DONE", "PROCESSING", "UNINITIALIZED", "FAILED"]
    :param m: starting index (default: 0)
    :param n: ending index (default: 10)
    :return: records with the provided status of analysis
    """
    app.app_context().push()
    with app.app_context():
        query = VideoData.query.filter_by(status=status)
        total_count = query.count()
        result = query.all()
        return result[m:n] if n <= total_count else result[m:total_count]


def set_status(
        app,
        file_hash: str,
        status: STATUS
):
    app.app_context().push()
    with app.app_context():
        v = VideoData.query.filter_by(file_hash=file_hash).first()
        v.status = status
        sql_db.session.commit()
