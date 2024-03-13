import os

from flask import Blueprint, request, render_template, make_response, session

from app.constants import DB_FOLDER
from app.tasks import make_file
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
        video_file = VideoParser(file, db_folder=DB_FOLDER)

        if not session.get('upload_list'):
            session.__setitem__("upload_list", [video_file.file_hash])
        else:
            session['upload_list'].append(video_file.file_hash)

        return make_response(("File uploaded successfully!", 200))

    elif request.method == 'GET':
        return render_template('upload.html')


@bp.route('/progress', methods=['GET', 'POST'])
def progress():
    """
    Route for progress of video analysis.

    :return: rendered HTML template `progress.html`
    """
    return render_template('progress.html')
