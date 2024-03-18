import os

from flask import Blueprint, request, render_template, make_response, session

from app.constants import DB_FOLDER
from app.tasks import make_file
from app.models import VideoData
from app.video_parser import VideoParser

bp = Blueprint("all", __name__)
"Global blueprint for all routes starting with /"


@bp.route("/<string:fname>/<string:content>")
def makefile(fname, content):
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    make_file.delay(fpath, content)
    return f"Find your file @ <code>{fpath}</code>"


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    """
    Route for the index page or the first landing page.

    :return: rendered HTML template `index.html`
    """
    return render_template('index.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Route for uploading videos.

    :return:
        GET  : rendered HTML template `upload.html`.
        POST : (response message, response integer).
    """
    if request.method == 'POST':
        file = request.files['file']
        video_file = VideoParser(file)
        ea = EmotionAnalyzer(video_file)
        emotion_analysis_task_manager.add_task(ea)

        session.__setitem__("latest_upload", video_file.file_hash)

        print(session.get('latest_upload'))
        sql_vd = VideoData(
            file_hash=video_file.file_hash,
            frames_processed=0,
            total_frames=video_file.total_frames,
            original_filename=video_file.video_file_path.name,
            status="UNINITIALIZED"
        )
        sql_db.session.add(sql_vd)
        sql_db.session.commit()

        return make_response(("File Uploaded Successfully", 200))

    elif request.method == 'GET':
        return render_template('upload.html')


@bp.route('/progress', methods=['GET', 'POST'])
def progress():
    """
    Route for progress of video analysis.

    :return: rendered HTML template `progress.html`
    """
    return render_template('progress.html')
