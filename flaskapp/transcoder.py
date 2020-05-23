import ffmpeg_streaming

from celery import Celery
from celery.app import push_current_task, pop_current_task
from celery.decorators import task
from ffmpeg_streaming import Formats
from pathlib import Path

# TODO Add logging where print()s are used

MEDIA_ROOT = Path('/srv/media/')  # TODO common config with app.py
DASH_MPD_FILENAME = 'dash.mpd'

celery = Celery('transcode')
celery.config_from_object('celeryconfig')


@task(name="transcode_video", bind=True)
def transcode_video(self, original_video_path, output_video_id):
    output_dir = MEDIA_ROOT / output_video_id
    try:
        output_dir.mkdir()
    except FileExistsError:
        print("Video with id '%s' already exists" % output_video_id)
        return

    def monitor(ffmpeg, duration, time):
        push_current_task(self)
        self.update_state(state='PROGRESS',
                          meta={'time': time, 'duration': duration})
        pop_current_task()

    input_video = ffmpeg_streaming.input(original_video_path)
    dash = input_video.dash(Formats.h264())
    dash.auto_generate_representations()
    dash.output(str(output_dir / DASH_MPD_FILENAME), monitor=monitor)
    
    # TODO return video ID for redirect here