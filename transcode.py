import ffmpeg_streaming
import functools
import json
import sys
import os
import pyinotify
import argparse

from ffmpeg_streaming import Formats 
from multiprocessing import Process, Queue
from pathlib import Path

# Local imports
import video_status

# TODO Add logging where print()s are used

MEDIA_ROOT = Path('runtime/media/')
DASH_MPD_FILENAME = 'dash.mpd'

def transcode(original_mp4_path, output_video_id):
    output_dir = MEDIA_ROOT / output_video_id
    try:
        output_dir.mkdir()
    except FileExistsError:
        print("Video with id '%s' already exists" % output_video_id)
        return

    input_video = ffmpeg_streaming.input(original_mp4_path)
    dash = input_video.dash(Formats.h264())
    dash.auto_generate_representations()
    dash.output(str(output_dir / DASH_MPD_FILENAME))

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--input', type=str)
parser.add_argument('--output', type=str)


if __name__ == '__main__':
    args = parser.parse_args()

    transcode(args.input, args.output)

    