from flask import Blueprint, request, render_template, session, make_response, redirect, url_for, send_file, jsonify

from app.factory import sql_db, emotion_analysis_task_manager
from app.forms import ConfigureAnalysisSettingsForm, ConfigurePeopleForm
from app.models import VideoData
from app.video_parser import EmotionAnalyzer
from app.video_parser import VideoParser

bp = Blueprint("all", __name__)
"Global blueprint for all routes starting with /"


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
        POST : (response message, response integer) | redirect.
    """

    if request.method == 'POST':
        print("SAVE FILE")
        file = request.files['file']
        video_file = VideoParser(file)
        ea = EmotionAnalyzer(video_file)
        emotion_analysis_task_manager.add_task(ea)
        print(video_file.video_dir)

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


@bp.route('/analysis_settings', methods=['GET', 'POST'])
def analysis_settings():
    return render_template("settings_analysis.html")


@bp.route('/people_config', methods=['GET', 'POST'])
def people_config():
    try:
        start = int(request.args.get('start'))
        end = int(request.args.get('end'))
    except TypeError:
        start = 0
        end = 10

    tasks = emotion_analysis_task_manager.get_tasks(start, end)
    print(tasks, end="\n")

    return render_template(
        "settings_people.html",
        tasks=tasks
    )


@bp.route('/get_image', methods=['POST'])
def get_image():
    file_hash = request.args.get('file_hash')
    img_index = int(request.args.get('img_index'))
    img_b64 = VideoParser.get_image_from_hash_index(file_hash, img_index)
    # return jsonify({"image":})
    # return send_file(
    #     img_io,
    #     mimetype='image/jpeg',
    #     as_attachment=False,
    #     download_name='person_%s.jpg' % img_index
    # )


@bp.route('/progress', methods=['GET', 'POST'])
def progress():
    """
    Route for progress of video analysis.

    :return: rendered HTML template `progress.html`
    """
    return render_template('progress.html')


# for job_id, arg in [
#     ("job_done", "DONE"),
#     ("job_proc", "PROCESSING"),
#     ("job_uninit", "UNINITIALIZED"),
#     ("job_fail", "FAILED")
# ]:
#     scheduler.add_job(id=job_id, trigger="interval", func=get_file_by_status, args=[arg], seconds=5)
