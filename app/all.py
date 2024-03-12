from flask import Blueprint, request, render_template, make_response
import os

from app.constants import DB_FOLDER
from app.tasks import make_file

bp = Blueprint("all", __name__)


@bp.route("/<string:fname>/<string:content>")
def makefile(fname, content):
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    make_file.delay(fpath, content)
    return f"Find your file @ <code>{fpath}</code>"


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload the recorded candidate video"""
    if request.method == 'POST':
        file = request.files['file']
        file.save(os.path.join(DB_FOLDER, file.filename))
        print("File saved:", file.filename)
        return make_response(("File uploaded successfully!", 200))

    elif request.method == 'GET':
        return render_template('upload.html')
