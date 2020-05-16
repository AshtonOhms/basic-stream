import json
import os

from flask import Flask, request, send_from_directory, flash, request, redirect, url_for
from werkzeug.utils import secure_filename



# Statics
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4'}

# Flask app config
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class MetadataStore:
    def __init__(self):
        pass

    def _get_metadata_path(video_id):
        return 'metadata/%s.json' % video_id

    def get_metadata(video_id):
        return json.load(_get_metadata_path(video_id))

    def update_metadata(video_id, metadata):
        json.dump(_get_metadata_path(video_id), metadata)


@app.route('/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


# Stuff for uploading
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            return redirect('index.html')

    return send_from_directory('static', 'upload.html')
