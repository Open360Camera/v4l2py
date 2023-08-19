"""
Example of multiplanar capture via rkisp device with
natice h264 encoding.
"""

import logging
import subprocess

from v4l2py import Device
from v4l2py.device import BufferType, VideoCapture

logging.basicConfig(level=logging.INFO)


command = 'gst-launch-1.0 fdsrc fd=0 ' \
          '! queue ' \
          '! rawvideoparse width=4048 height=3040 format=nv12 ' \
          '! mpph264enc ' \
          '! h264parse ' \
          '! mp4mux ' \
          '! filesink location=./v1.mp4'


process = subprocess.Popen(
    command, shell=True, stdin=subprocess.PIPE)

with Device('/dev/video11') as cam:
    logging.info(cam.info)
    cam.set_format(BufferType.VIDEO_CAPTURE_MPLANE, 4040, 3040, 'NV12')

    video = VideoCapture(device=cam, buffer_type=BufferType.VIDEO_CAPTURE_MPLANE)
    with video as stream:
        for i, frame in enumerate(stream):

            logging.info('Received frame with length %s', len(frame.data))
            process.stdin.write(frame.data)
            process.stdin.flush()

            if i > 200:
                break
    process.stdin.close()

process.wait()