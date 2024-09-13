from logging import Logger
from threading import Thread

import cv2
import numpy as np

from utils.utils import exception_handler


class Source:
    def __init__(self, source, logger_err: Logger, resize_factor=1) -> None:
        self.source = source
        self.cap = cv2.VideoCapture(source)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // resize_factor
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // resize_factor
        self.width = int(self.width)
        self.height = int(self.height)
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.resize_factor = resize_factor
        self.logger_err = logger_err

    def release(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def __iter__(self):
        return self


class VideoSource(Source):
    def __init__(self, path, logger_err, resize_factor=1) -> None:
        super().__init__(path, logger_err, resize_factor)

    def __next__(self):
        self.cap.grab()
        retval, image = self.cap.retrieve()

        if not retval:
            raise StopIteration

        if self.resize_factor != 1:
            image = cv2.resize(
                image,
                (0, 0),
                fx=1 / self.resize_factor,
                fy=1 / self.resize_factor,
            )

        return True, image


class StreamSource(Source):
    def __init__(self, url, logger_err: Logger, resize_factor=1) -> None:
        super().__init__(url, logger_err, resize_factor)
        self.url = url
        self.logger_err = logger_err
        self.thread = Thread(target=self.update, args=(), daemon=True)
        self.thread.start()
        self.current_frame = None

    def __next__(self):
        if not self.thread.is_alive():
            raise StopIteration

        if self.current_frame is None:
            return False, np.zeros((self.height, self.width, 3), dtype=np.uint8)

        image = self.current_frame

        if self.resize_factor != 1:
            image = cv2.resize(
                image,
                (0, 0),
                fx=1 / self.resize_factor,
                fy=1 / self.resize_factor,
            )

        return True, image

    @exception_handler
    def update(self):
        while self.cap.isOpened():
            while self.try_grab():
                pass

            retval, image = self.cap.retrieve()
            if retval:
                # self.frames.put(image)
                self.current_frame = image
            else:
                self.cap.open(self.url)

    def try_grab(self):
        try:
            self.cap.grab()
            return False
        except Exception as e:
            self.logger_err.error(e, exc_info=True)
            self.cap.release()
            self.cap.open(self.url)
            return True
