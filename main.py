import json
import os

from flask import Flask, request, \
    send_from_directory, flash, redirect, url_for, render_template
from pathlib import Path
from werkzeug.utils import secure_filename


# Statics
RUNTIME_DIR = Path('runtime')
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
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = str(UPLOADS_DIR) # TODO should be in app.config? name?


# TODO get rid of this, serve statics correctly
@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


@app.route('/watch/<video_id>')
def watch_page(video_id):
    dash_mpd_url = MEDIA_DIR / video_id / DASH_MPD_FILENAME

    return render_template('watch.jinja2', dash_mpd_url=dash_mpd_url)

@app.route('/')
def list_page():
    # Each video's DASH encodings will live in a directory in
    # the media directory
    video_dirs = [path for path in MEDIA_DIR.iterdir() if path.is_dir()]

    video_ids = [str(video_dir) for video_dir in video_dirs]

    return render_template('list.jinja2', video_ids=video_ids)


# Stuff for uploading
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
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