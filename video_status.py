from filelock import FileLock
from os import listdir
from os.path import isfile, join
from pathlib import Path

STATUS_DIR = 'status'

def _get_status_path(video_name):   
    return Path(STATUS_DIR, video_name + ".status")

def update_status(video_name, status):
    status_path = _get_status_path(video_name)

    with FileLock(str(status_path) + ".lock"):
        open(status_path, "w+").write(status)

def read_status(video_name):
    status_path = _get_status_path(video_name)

    with FileLock(str(status_path) + ".lock"):
        with open(status_path, "r") as sf:
            return sf.read()

# Determine video names from the list of status files
def get_videos():
    return [f.rsplit(".", 1) for f in os.listdir(STATUS_DIR) if f.endswith('.stat')]
 