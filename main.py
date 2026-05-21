import sys
import time
import cv2

import config
from camera import open_camera
from pose_detector import PoseDetector
from posture_analyzer import PostureAnalyzer
from notifier import Notifier
from display import draw_overlay


def main() -> None:
    detector = PoseDetector(
        min_detection_confidence=config.MEDIAPIPE_DETECTION_CONFIDENCE,
        min_tracking_confidence=config.MEDIAPIPE_TRACKING_CONFIDENCE,
    )
    analyzer = PostureAnalyzer(
        shoulder_tilt_tolerance=config.SHOULDER_TILT_TOLERANCE,
        ear_tilt_tolerance=config.EAR_TILT_TOLERANCE,
        neck_gap_tolerance=config.NECK_GAP_TOLERANCE,
        head_drop_tolerance=config.HEAD_DROP_TOLERANCE,
    )
    notifier = Notifier(cooldown=config.NOTIFICATION_COOLDOWN)

    last_check = 0.0
    last_report = None

    print("Posture Checker running.")
    print("  q  — quit")
    print("  c  — calibrate (sit straight, then press c)")

    with open_camera(config.CAMERA_INDEX, config.FRAME_WIDTH, config.FRAME_HEIGHT) as cap:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read from camera.", file=sys.stderr)
                break

            frame = cv2.flip(frame, 1)  # mirror so left/right feel natural
            results = detector.detect(frame)
            now = time.time()

            if now - last_check >= config.CHECK_INTERVAL:
                last_report = analyzer.analyze(results.pose_landmarks)
                last_check = now
                if last_report and not last_report.is_good:
                    notifier.notify(last_report.issues)

            draw_overlay(frame, results, last_report, detector, analyzer.is_calibrated)
            cv2.imshow("Posture Checker", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("c"):
                _calibrate(analyzer, results)

    detector.close()
    cv2.destroyAllWindows()


def _calibrate(analyzer: PostureAnalyzer, results) -> None:
    if analyzer.calibrate(results.pose_landmarks):
        print("Calibration saved — this is now your good-posture baseline.")
    else:
        print("Calibration failed: no pose detected, move into frame and try again.")


if __name__ == "__main__":
    main()
