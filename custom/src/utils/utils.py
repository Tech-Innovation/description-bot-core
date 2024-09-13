from threading import Thread
import time
from enum import Enum

import cv2


class Color(Enum):
    # monochromatic
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    # primary
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLUE = (255, 0, 0)
    # secondary
    YELLOW = (0, 255, 255)
    PURPLE = (255, 0, 255)
    CYAN = (255, 255, 0)
    # tertiary
    ORANGE = (0, 128, 255)
    PINK = (255, 128, 0)
    BROWN = (0, 128, 128)


class RefPoint(Enum):
    BL = 1
    TL = 2
    TR = 3
    BR = 4
    C = 5


def customPutText(
    img,
    text,
    org,
    font_face,
    font_scale,
    color,
    thickness,
    **kwargs,
):
    (text_width, text_height), _ = cv2.getTextSize(text, font_face, font_scale, thickness)

    padding = 5

    ref_point = kwargs.get("ref_point", None)
    background_color = kwargs.get("background_color", None)
    text_org = org

    if ref_point:
        if ref_point == RefPoint.TL.name:
            text_org = (org[0], org[1] + text_height)

        if ref_point == RefPoint.TR.name:
            text_org = (org[0] - text_width, org[1] + text_height)

        if ref_point == RefPoint.BR.name:
            text_org = (org[0] - text_width, org[1])

        if ref_point == RefPoint.C.name:
            text_org = (org[0] - text_width // 2, org[1] + text_height // 2)

    if background_color:
        p2 = (org[0] + text_width, org[1] - text_height)
        if ref_point:
            if ref_point == RefPoint.TL.name:
                p2 = (org[0] + text_width, org[1])

            if ref_point == RefPoint.TR.name:
                p2 = (org[0], org[1])

            if ref_point == RefPoint.BR.name:
                p2 = (org[0], org[1] - text_height)

            if ref_point == RefPoint.C.name:
                p2 = (org[0] + text_width // 2, org[1] - text_height // 2)

        cv2.rectangle(
            img,
            (text_org[0] - padding, text_org[1] + padding),
            (p2[0] + padding, p2[1] - padding),
            background_color,
            cv2.FILLED,
        )

    cv2.putText(img, text, text_org, font_face, font_scale, color, thickness, cv2.FILLED)


def custom_show(img, name="img", resize=False, resize_factor=0.5):
    if resize:
        cv2.imshow(name, cv2.resize(img, (0, 0), fx=resize_factor, fy=resize_factor))
        return

    cv2.imshow(name, img)


def get_now_str():
    current_time = time.localtime()
    formatted_datetime = time.strftime("%Y-%m-%d_%H-%M-%S", current_time)

    # Create a filename using the formatted date and time
    filename = f"{formatted_datetime}"

    return filename


def get_now_formatted_str():
    current_time = time.localtime()
    formatted_datetime = time.strftime("%d/%m/%Y %H:%M:%S", current_time)

    return formatted_datetime


def exception_handler(f):
    def wrapper(*args):
        try:
            f(*args)
        except Exception as e:
            args[0].logger_err.error(f"Error en {f.__name__}: {e}", exc_info=True)

    return wrapper


def async_func(f):
    def wrapper(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()

    return wrapper
