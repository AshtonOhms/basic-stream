from filelock import FileLock
from os import listdir
from os.path import isfile, join
from pathlib import Path

STATUS_DIR = 'status'

def _get_status_path(video_name):   
    return Path(STATUS_DIR, video_name + ".status")

def _get_lock(status_path):
    return FileLock(str(status_path) + ".lock")

def update_status(video_name, status):
    status_path = _get_status_path(video_name)

    with _get_lock(status_path):
        with open(status_path, "w+") as sf:
            sf.write(status)

def read_status(video_name):
    status_path = _get_status_path(video_name)

    with _get_lock(status_path):
        with open(status_path, "r") as sf:
            return sf.read()

# Determine video names from the list of status files
def get_videos():
    return [f.rsplit(".", 1) for f in os.listdir(STATUS_DIR) if f.endswith('.stat')]
 