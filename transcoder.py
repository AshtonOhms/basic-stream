import ffmpeg_streaming

from celery import Celery
from celery.decorators import task
from ffmpeg_streaming import Formats 
from multiprocessing import Process, Queue
from pathlib import Path

# TODO Add logging where print()s are used

MEDIA_ROOT = Path('/srv/media/') # TODO common config with app.py
DASH_MPD_FILENAME = 'dash.mpd'

celery = Celery('transcode')

@task(name="transcode")
def transcode(original_video_path, output_video_id):
    output_dir = MEDIA_ROOT / output_video_id
    try:
        output_dir.mkdir()
    except FileExistsError:
        print("Video with id '%s' already exists" % output_video_id)
        return

    input_video = ffmpeg_streaming.input(original_video_path)
    dash = input_video.dash(Formats.h264())
    dash.auto_generate_representations()
    dash.output(str(output_dir / DASH_MPD_FILENAME))
    