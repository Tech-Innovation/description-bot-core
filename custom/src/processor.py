from configuration.config import Inputs, Params
from clients.streaming import StreamingClient
from Analyser import Analyser
from Source import StreamSource, VideoSource
from utils.utils import async_func
from utils.constants import CAMERA_IP_PROTOCOLS


class Processor:
    def __init__(self, inputs: Inputs, streaming_client: StreamingClient, params: Params) -> None:
        self.running = True
        self.resize_factor = 1

        self.source = (
            StreamSource(inputs.source, self.resize_factor)
            if inputs.source.startswith(CAMERA_IP_PROTOCOLS)
            else VideoSource(inputs.source, self.resize_factor)
        )

        self.streaming_client = streaming_client
        self.model = params.model
        self.query = params.query

    def set_analyser(self):
        self.analyser = Analyser(self.model, self.query)

    @async_func
    def process_frame(self, frame):
        self.description = self.analyser.analyse(frame)
        self.streaming_client.send_message(self.description)
        print(self.description)

    def run(self):
        self.running = True

        self.set_analyser()

        self.frame = None
        self.description = None

        for ret, frame in self.source:

            if not ret:
                continue

            if not self.running:
                break

            self.frame = frame

            self.process_frame(frame)

            self.streaming_client.send_frame(frame)

        self.source.release()
