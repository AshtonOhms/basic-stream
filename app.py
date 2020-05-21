import string

from celery.result import AsyncResult
from flask import Flask, request, \
    send_from_directory, flash, redirect, url_for, render_template, jsonify #TODO alphabetize
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, UserManager, UserMixin
from pathlib import Path
from werkzeug.utils import secure_filename

# Local imports
import sessions
import transcoder

# Statics
SERVER_ROOT = Path('/srv')
SQLITE_DB = SERVER_ROOT / 'sqlite' / 'app.sqlite'
UPLOADS_DIR = SERVER_ROOT / 'uploads'
MEDIA_DIR = SERVER_ROOT / 'media'
DASH_MPD_FILENAME = 'dash.mpd'
ALLOWED_EXTENSIONS = {'mp4'}

DIRS_TO_CREATE = (
    UPLOADS_DIR,
    MEDIA_DIR
)


# Flask app config
class ConfigClass(object):
    UPLOAD_FOLDER = str(UPLOADS_DIR)
    
    # Flask settings
    SECRET_KEY = 'some_secret_TODO_changethis' # change to str >=32 bytes
    TEMPLATES_AUTO_RELOAD = True

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///%s' % str(SQLITE_DB)    # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Some Video Website Idk"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False      # Disable email authentication
    USER_ENABLE_CONFIRM_EMAIL = False
    USER_ENABLE_USERNAME = True    # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form


# TODO move this app/db instantiation out of top-level
app = Flask(__name__)
app.config.from_object(__name__+'.ConfigClass')
db = SQLAlchemy(app)


# Set up user model for Flask-User
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')


db.create_all()

user_manager = UserManager(app, db, User)


# TODO get rid of this, serve statics via nginx?
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


# TODO get rid of this, serve media via nginx?
@app.route('/media/<video_id>/<path>')
def serve_dash(video_id, path):
    video_dir = MEDIA_DIR / video_id

    return send_from_directory(video_dir, path)


# Called by nginx to authenticate requests for media
@app.route("/auth")
def nginx_auth():
    if current_user.is_authenticated:
        return "auth passed"
    else:
        return 'auth failed', 401

# Routes for watching


@app.route('/watch/<video_id>')
@login_required
def watch_page(video_id):
    session_id = sessions.create_session(video_id)

    return redirect("/session/%s" % session_id)


@app.route('/session/<session_id>')
@login_required
def watch_session(session_id):
    video_id = sessions.get_session_video_id(session_id)

    dash_mpd_url = "/media/%s/%s" % (video_id, DASH_MPD_FILENAME) # TODO configure 'media' path elsewhere

    return render_template('watch.jinja2',
                           session_id = session_id,
                           dash_mpd_url=dash_mpd_url)


@app.route('/session/<session_id>/time', methods=['POST'])
@login_required
def post_watch_status(session_id):
    # TODO Implement
    time = 0

    sessions.set_user_status(session_id, time)


@app.route('/')
@login_required
def browse_page():
    # Each video's DASH encodings will live in a directory in
    # the media directory
    video_dirs = [path for path in MEDIA_DIR.iterdir() if path.is_dir()]

    video_ids = [video_dir.name for video_dir in video_dirs]

    videos = [{
        "video_id": video_id,
        "poster_url": "/media/%s/poster.png" % video_id
    } for video_id in video_ids]

    return render_template('browse.jinja2', videos=videos)


@app.route('/transcode/<task_id>')
@login_required
def transcode_status_page(task_id):
    return render_template('transcode.jinja2')


@app.route('/transcode/<task_id>/status')
@login_required
def transcode_status(task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        # Not yet started
        response = {
            'state': task.state,
            'time': 0,
            'duration': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'time': task.info.get('time', 0),
            'duration': task.info.get('duration', 1),
            'status': 'Transcoding...'
        }
    else:
        # Failure!
        response = {
            'state': task.state,
            'time': 1,
            'duration': 1,
            'status': str(task.info) # This is the exception
        }

    return jsonify(response)

# Stuff for uploading
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part') # TODO what does `flash()` do?
            return redirect(request.url)
        file = request.files['file']

        if 'title' not in request.form:
            flash('No id provided')
            return redirect(request.url)
        title = request.form['title']

        # TODO make video ID generation better
        valid_chars = string.ascii_lowercase + string.digits
        video_id = "".join([c for c in title.replace(" ", "_").lower() if c in valid_chars])

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = str(UPLOADS_DIR / filename)

            # TODO this relies on the fact that the transcode container
            # gets the same /srv/upload and /srv/media mounts as the transcoder,
            # fix this by making it relative to the respective roots?
            file.save(filepath)

            # Enqueue celery task to transcode
            task = transcoder.transcode_video.delay(filepath, video_id)

            return redirect('/transcode/%s' % task.id)  # TODO redirect to a static page

    return render_template('upload.jinja2')


if __name__ == '__main__':
    # Set up our directories
    for dir_path in DIRS_TO_CREATE:
        dir_path.mkdir(exist_ok=True)

    app.run(debug=True)