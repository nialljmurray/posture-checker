import subprocess
import sys
import time
from pathlib import Path

import cv2
import mediapipe as mp

_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)
_MODEL_PATH = Path(getattr(sys, "_MEIPASS", Path(__file__).parent)) / "pose_landmarker_lite.task"

# Pairs of landmark indices to draw as skeleton lines
_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # arms
    (11, 23), (12, 24), (23, 24),                        # torso
    (23, 25), (25, 27), (24, 26), (26, 28),              # legs
    (0, 4), (4, 5), (5, 6), (6, 8),                      # face right
    (0, 1), (1, 2), (2, 3), (3, 7),                      # face left
    (9, 10),                                              # mouth
]

_GREEN = (0, 220, 0)
_BLUE = (255, 80, 0)


class PoseDetector:
    def __init__(self, min_detection_confidence: float, min_tracking_confidence: float):
        _ensure_model()

        options = mp.tasks.vision.PoseLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(_MODEL_PATH)),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            min_pose_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self._landmarker = mp.tasks.vision.PoseLandmarker.create_from_options(options)

    def detect(self, frame):
        """Run pose estimation on a BGR frame. Returns a PoseLandmarkerResult."""
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int(time.monotonic() * 1000)
        return self._landmarker.detect_for_video(mp_image, timestamp_ms)

    def draw_landmarks(self, frame, results) -> None:
        if not results.pose_landmarks:
            return
        h, w = frame.shape[:2]
        landmarks = results.pose_landmarks[0]

        for start_idx, end_idx in _CONNECTIONS:
            if start_idx >= len(landmarks) or end_idx >= len(landmarks):
                continue
            a, b = landmarks[start_idx], landmarks[end_idx]
            if a.visibility > 0.5 and b.visibility > 0.5:
                cv2.line(
                    frame,
                    (int(a.x * w), int(a.y * h)),
                    (int(b.x * w), int(b.y * h)),
                    _GREEN, 2, cv2.LINE_AA,
                )

        for lm in landmarks:
            if lm.visibility > 0.5:
                cv2.circle(frame, (int(lm.x * w), int(lm.y * h)), 4, _BLUE, -1)

    def close(self) -> None:
        self._landmarker.close()


def _ensure_model() -> None:
    if _MODEL_PATH.exists():
        return
    print("Downloading pose model — one-time setup (~3 MB)...")
    result = subprocess.run(
        ["curl", "-fL", "-o", str(_MODEL_PATH), _MODEL_URL],
        capture_output=True,
    )
    if result.returncode != 0:
        print(result.stderr.decode(), file=sys.stderr)
        raise RuntimeError("Failed to download pose model.")
    print("Model downloaded.")
