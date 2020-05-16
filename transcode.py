import ffmpeg_streaming
import functools
import json
import sys
import os
import pyinotify

from ffmpeg_streaming import Formats 
from multiprocessing import Process, Queue
from pathlib import Path

# Local imports
import video_status

# TODO Add logging where print()s are used

UPLOAD_ROOT = "uploads"
TRANSCODE_ROOT = "transcode"
TRANSCODE_OUTPUT_NAME = "dash.mpd"

def transcode_process(queue):
    while True:
        message = queue.get(block=True)

        if message['type'] == 'video_uploaded':
            path = message['path']

            print("Transcoding " + path)

            # Get the file name w/out the path
            video_filename = os.path.split(path)[1]

            # Remove extension
            video_name = video_filename.rsplit('.', 1)[0]

            # Create transcode output directory
            transcode_dir = Path(TRANSCODE_ROOT, video_name)

            # Create status file with TRANSCODING status
            video_status.update_status(video_name, "TRANSCODING")

            # Transcode the video
            input_video = ffmpeg_streaming.input(path)
            dash = input_video.dash(Formats.h264())
            dash.auto_generate_representations()
            dash.output(str(transcode_dir / TRANSCODE_OUTPUT_NAME))

            video_status.update_status(video_name, "DONE")
        else:
            print('Unsupported message type %s' % message['type'])


class UploadCreationHandler(pyinotify.ProcessEvent):
    def my_init(self, queue):
        self.queue = queue

    def process_default(self, event):
        if event.dir:
            print('Directory created, ignoring')
            return

        print('Recieved file event %s' % str(event))
        self.queue.put({
                'type': 'video_uploaded',
                'path': event.pathname
            })

if __name__ == '__main__':
    queue = Queue()

    # Start the event processor
    reader_p = Process(target=transcode_process, args=((queue),))
    reader_p.daemon = True
    reader_p.start()
    print("Transcode handler started")

    # Start the file watch (emits events)
    wm = pyinotify.WatchManager()
    # It is important to pass named extra arguments like 'fileobj'.
    handler = UploadCreationHandler(queue=queue)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(UPLOAD_ROOT, pyinotify.IN_CREATE)
    print("Starting file system watch")
    notifier.loop()
    