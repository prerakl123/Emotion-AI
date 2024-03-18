from flask import Blueprint, request, render_template, session, make_response, redirect, url_for

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
        POST : (response message, response integer).
    """
    cas_form = ConfigureAnalysisSettingsForm()
    cp_form = ConfigurePeopleForm()

    if cas_form.validate_on_submit():
        return redirect(url_for("all.analysis_settings"))

    if cp_form.validate_on_submit():
        return redirect(url_for("all.people_config"))

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
        return render_template('upload.html', cas_form=cas_form, cp_form=cp_form)


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
