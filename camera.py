import sys
from contextlib import contextmanager
import cv2


@contextmanager
def open_camera(index: int, width: int, height: int):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        print(f"Error: could not open camera at index {index}.", file=sys.stderr)
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    try:
        yield cap
    finally:
        cap.release()
