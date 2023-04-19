#
# This file is part of the v4l2py project
#
# Copyright (c) 2023 Tiago Coutinho
# Distributed under the GPLv3 license. See LICENSE for more info.

# Extra dependencies required to run this example:
# pip install fastapi jinja2 python-multipart cv2 pillow uvicorn

# run from this directory with:
# uvicorn async:app

"""Common tools for async and sync web app examples"""

import io

import cv2
import PIL.Image

from v4l2py.device import Device, PixelFormat, VideoCapture


BOUNDARY = "frame"
HEADER = (
    "--{boundary}\r\nContent-Type: image/{type}\r\nContent-Length: {length}\r\n\r\n"
)
SUFFIX = b"\r\n"


class BaseCamera:
    def __init__(self, device: Device) -> None:
        self.device: Device = device
        self.capture: VideoCapture = VideoCapture(self.device)
        with device:
            self.info = self.device.info


def frame_to_image(frame, output="jpeg"):
    match frame.pixel_format:
        case PixelFormat.JPEG | PixelFormat.MJPEG:
            if output == "jpeg":
                return to_image_send(frame.data, type=output)
            else:
                buff = io.BytesIO()
                image = PIL.Image.open(io.BytesIO(frame.data))
        case PixelFormat.GREY:
            data = frame.array
            data.shape = frame.height, frame.width, -1
            image = PIL.Image.frombuffer("L", (frame.width, frame.height), data)
        case PixelFormat.YUYV:
            data = frame.array
            data.shape = frame.height, frame.width, -1
            rgb = cv2.cvtColor(data, cv2.COLOR_YUV2RGB_YUYV)
            image = PIL.Image.fromarray(rgb)

    buff = io.BytesIO()
    image.save(buff, output)
    return to_image_send(buff.getvalue(), type=output)


def to_image_send(data, type="jpeg", boundary=BOUNDARY):
    header = HEADER.format(type=type, boundary=boundary, length=len(data)).encode()
    return b"".join((header, data, SUFFIX))