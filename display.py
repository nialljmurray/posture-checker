import cv2
from typing import Optional
from posture_analyzer import PostureReport

_GREEN = (0, 200, 0)
_RED = (0, 60, 220)
_YELLOW = (0, 200, 255)
_WHITE = (255, 255, 255)
_DARK = (30, 30, 30)

_FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_overlay(frame, results, report: Optional[PostureReport], detector, calibrated: bool) -> None:
    detector.draw_landmarks(frame, results)
    _draw_status_bar(frame, report, calibrated)


def _draw_status_bar(frame, report: Optional[PostureReport], calibrated: bool) -> None:
    h, w = frame.shape[:2]
    bar_h = 56
    cv2.rectangle(frame, (0, h - bar_h), (w, h), _DARK, -1)

    if report is None:
        _text(frame, "No pose detected — move into frame", (12, h - 18), _YELLOW, 0.6)
        return

    if report.is_good:
        status_color = _GREEN
        status_text = "Good posture"
    else:
        status_color = _RED
        status_text = "  ".join(report.issues)

    _text(frame, status_text, (12, h - 28), status_color, 0.65, thickness=2)

    metrics = (
        f"Shoulder tilt: {report.shoulder_tilt:.3f}  "
        f"Ear tilt: {report.ear_tilt:.3f}  "
        f"Neck gap: {report.neck_gap:.3f}  "
        f"Head drop: {report.head_drop:.3f}"
    )
    _text(frame, metrics, (12, h - 8), _WHITE, 0.45)

    calib_label = "Calibrated" if calibrated else "Press 'c' to calibrate"
    calib_color = _GREEN if calibrated else _YELLOW
    _text(frame, calib_label, (w - 240, h - 18), calib_color, 0.55)


def _text(frame, text: str, pos: tuple, color, scale: float, thickness: int = 1) -> None:
    cv2.putText(frame, text, pos, _FONT, scale, color, thickness, cv2.LINE_AA)
