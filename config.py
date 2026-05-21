CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# How often (in seconds) to evaluate posture
CHECK_INTERVAL = 3.0
# Minimum seconds between macOS notifications
NOTIFICATION_COOLDOWN = 10.0

# Posture deviation thresholds (normalized 0–1 units, relative to frame size).
# Applied as tolerance on top of the calibrated baseline.
# Before calibration they act as absolute thresholds.

# Desk-use thresholds — tighter than general use.
SHOULDER_TILT_TOLERANCE = 0.025   # uneven shoulders
EAR_TILT_TOLERANCE      = 0.025   # head tilted left/right
NECK_GAP_TOLERANCE      = 0.03    # shoulders rising toward ears (hunching)
HEAD_DROP_TOLERANCE     = 0.02    # nose dropping toward shoulder level (looking down)

MEDIAPIPE_DETECTION_CONFIDENCE = 0.7
MEDIAPIPE_TRACKING_CONFIDENCE  = 0.7
