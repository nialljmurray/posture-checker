# Posture Checker

A real-time posture monitoring tool for macOS that uses your MacBook's built-in camera and MediaPipe Pose to detect and alert you about bad sitting posture.

---

## How It Works — From the User's Perspective

1. **Run the app** (`python main.py`). A live camera window opens showing your webcam feed with a skeleton overlay drawn on your body.
2. **Calibrate** — sit up straight and press `c`. The app records your current body position as your good-posture baseline.
3. **Keep working** — the app runs quietly in the background. Every 3 seconds it re-evaluates your posture.
4. **Get notified** — if bad posture is detected, a native macOS notification appears (e.g. *"Shoulders are raised — you may be hunching"*). Notifications won't spam you; there is a 60-second cooldown between alerts.
5. **Status bar** — the bottom of the video window always shows the current assessment and live metric values.
6. **Quit** — press `q` to exit.

---

## How It Works — From the Code's Perspective

### Architecture

The project is split into focused, single-responsibility modules:

```
main.py              — Entry point and main loop
config.py            — All tuneable constants (thresholds, intervals, camera settings)
camera.py            — Context-manager wrapper around OpenCV camera capture
pose_detector.py     — MediaPipe Pose inference wrapper
posture_analyzer.py  — Posture metric calculation and calibration logic
notifier.py          — macOS system notifications (via osascript)
display.py           — On-frame overlay rendering (status bar, metrics, landmarks)
```

### Pipeline (one frame)

```
cap.read()
   └─► PoseDetector.detect()          # BGR → RGB, MediaPipe Pose inference
           └─► PostureAnalyzer.analyze()   # compute metrics, compare to baseline
                   └─► Notifier.notify()       # send macOS alert if cooldown allows
draw_overlay()                         # render landmarks + status bar onto frame
cv2.imshow()                           # display to user
```

### Pose Detection (`pose_detector.py`)

Uses **MediaPipe Pose**, a lightweight ML model that returns 33 body landmarks (normalised 0–1 x/y coordinates + relative depth z). The frame is colour-converted to RGB before inference because MediaPipe expects RGB, then the results are handed back to the caller. The detector also provides `draw_landmarks()` which renders the skeleton using MediaPipe's built-in drawing utilities.

### Posture Analysis (`posture_analyzer.py`)

Three metrics are computed from four key landmarks — left/right shoulders and left/right ears:

| Metric | Formula | What it detects |
|---|---|---|
| **Shoulder tilt** | `abs(left_shoulder.y − right_shoulder.y)` | One shoulder raised higher than the other |
| **Ear tilt** | `abs(left_ear.y − right_ear.y)` | Head tilted to one side |
| **Neck gap** | `shoulder_mid.y − ear_mid.y` | Vertical distance between ear midpoint and shoulder midpoint — shrinks when hunching |

All coordinates are normalised (0–1), so the thresholds are resolution-independent.

**Before calibration**: metrics are compared against absolute threshold values from `config.py`.

**After calibration**: the recorded baseline is subtracted first, so only *changes* from your personal good-posture reference are flagged. This makes the detector robust to individual variation in body proportions and camera position.

### Calibration (`PostureAnalyzer.calibrate`)

Stores a `_Baseline` dataclass capturing the three metric values at the moment the user pressed `c`. Subsequent analyses compute `metric − baseline > tolerance` instead of `metric > tolerance`.

### Notifications (`notifier.py`)

Uses `subprocess` to call `osascript` (AppleScript), which triggers a native macOS notification:
```
osascript -e 'display notification "…" with title "Posture Check"'
```
A timestamp gate (`_last_sent`) enforces the cooldown so alerts are not repeated on every check.

### Display (`display.py`)

Draws a semi-transparent dark bar at the bottom of the frame containing:
- **Status text** (green = good, red = issue list)
- **Raw metric values** for debugging/tuning
- **Calibration state** indicator

---

## Setup

```bash
pip install -r requirements.txt
python main.py
```

macOS will ask for camera permission on first run — allow it.

---

## Tuning

Edit `config.py` to adjust behaviour:

| Constant | Default | Effect |
|---|---|---|
| `CHECK_INTERVAL` | `3.0 s` | How often posture is evaluated |
| `NOTIFICATION_COOLDOWN` | `60.0 s` | Minimum gap between alerts |
| `SHOULDER_TILT_TOLERANCE` | `0.04` | Sensitivity to uneven shoulders |
| `EAR_TILT_TOLERANCE` | `0.04` | Sensitivity to head tilt |
| `NECK_GAP_TOLERANCE` | `0.05` | Sensitivity to hunching |

Smaller tolerance values = more sensitive (more alerts). Calibrating first is strongly recommended before tuning these.

---

## Limitations

- Detection works best with the upper body clearly visible and a plain background.
- Forward-head posture (head jutting toward the screen) is difficult to measure accurately from a purely frontal camera; the current metrics focus on shoulder and head tilt, which are the most reliably observable from a laptop webcam.
- The app must remain in the foreground for `cv2.waitKey` to register key presses, but the camera window can be moved aside — notifications will still arrive.
