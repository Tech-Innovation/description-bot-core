import base64
from dataclasses import dataclass
import uuid

from utils.utils import async_func
import cv2
import socketio


@dataclass
class StreamingConfig:
    """
    Configuration for the streaming client
    """

    enabled: bool
    url: str


class StreamingClient:
    """
    Client class for set communication with the streaming server (websockets).
    """

    def __init__(self, config: StreamingConfig):
        self.enabled = config.enabled
        self.url = config.url
        if self.enabled:
            self.sio = socketio.Client()
            self.sio.connect(config.url)

    @async_func
    def send_frame(self, frame):
        if not self.enabled:
            return

        _, buffer = cv2.imencode(".jpg", frame)
        frame_base64 = base64.b64encode(buffer).decode("utf-8")
        self.sio.emit(
            "data",
            {
                "frame_id": str(uuid.uuid4()),
                "frame": frame_base64,
                "frame_width": frame.shape[1],
                "frame_height": frame.shape[0],
            },
        )

    @async_func
    def send_message(self, message):
        if not self.enabled:
            return

        self.sio.emit("message", {"message": message})
