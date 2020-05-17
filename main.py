import json
import os

from flask import Flask, request, \
    send_from_directory, flash, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_user import login_required, UserManager, UserMixin
from pathlib import Path
from werkzeug.utils import secure_filename


# Statics
RUNTIME_DIR = Path('runtime')
SQLITE_DB = RUNTIME_DIR / 'app.sqlite'
UPLOADS_DIR = RUNTIME_DIR / 'upload'
MEDIA_DIR = RUNTIME_DIR / 'media'
DASH_MPD_FILENAME = 'dash.mpd'
ALLOWED_EXTENSIONS = {'mp4'}

DIRS_TO_CREATE = (
    RUNTIME_DIR,
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

@app.route('/watch/<video_id>')
@login_required
def watch_page(video_id):
    dash_mpd_url = "/media/%s/%s" % (video_id, DASH_MPD_FILENAME) # TODO configure 'media' path

    return render_template('watch.jinja2', dash_mpd_url=dash_mpd_url)

@app.route('/')
@login_required
def list_page():
    # Each video's DASH encodings will live in a directory in
    # the media directory
    video_dirs = [path for path in MEDIA_DIR.iterdir() if path.is_dir()]

    video_ids = [video_dir.name for video_dir in video_dirs]

    return render_template('list.jinja2', video_ids=video_ids)


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

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # TODO use pathlib.Path here

            return redirect('index.html')

    return send_from_directory('static', 'upload.html')


if __name__ == '__main__':
    # Set up our directories
    for dir_path in DIRS_TO_CREATE:
        dir_path.mkdir(exist_ok=True)

    app.run(debug=True)