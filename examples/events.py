from fcntl import ioctl

from v4l2py.device import EventType, Device
from v4l2py.raw import v4l2_event, \
    VIDIOC_DQEVENT

CIFISP_V4L2_EVENT_STREAM_START = EventType.PRIVATE_START + 1
CIFISP_V4L2_EVENT_STREAM_STOP = EventType.PRIVATE_START + 2


def wait_for_event(fd: int, event_type: int):
    event = v4l2_event()
    while True:
        ioctl(fd, VIDIOC_DQEVENT, event)

        if event.type == event_type:
            break


# open device manually to avoid issues with non-blocking io
with Device(open('/dev/video19')) as device:
    device.subscribe_event(CIFISP_V4L2_EVENT_STREAM_START)
    device.subscribe_event(CIFISP_V4L2_EVENT_STREAM_STOP)

    try:
        wait_for_event(device.fileno(), CIFISP_V4L2_EVENT_STREAM_START)
    finally:
        device.unsubscribe_event(CIFISP_V4L2_EVENT_STREAM_START)
        device.unsubscribe_event(CIFISP_V4L2_EVENT_STREAM_STOP)
