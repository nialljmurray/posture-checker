# Posture Checker

A real-time posture monitoring tool for macOS. Uses your MacBook's built-in camera and MediaPipe Pose to detect bad sitting posture and send native notifications.

---

## Features

- Live camera feed with skeleton overlay
- Detects uneven shoulders, head tilt, and hunching
- Native macOS notifications with a configurable cooldown
- Personal calibration — set your own good-posture baseline

## Setup

```bash
git clone https://github.com/nialljmurray/posture-checker.git
cd posture-checker
pip install -r requirements.txt
python main.py
```

macOS will prompt for camera permission on first run.

### Controls

| Key | Action |
|-----|--------|
| `c` | Calibrate — sit up straight first |
| `q` | Quit |

---

## Configuration

Edit `config.py` to tune sensitivity:

| Constant | Default | Effect |
|---|---|---|
| `CHECK_INTERVAL` | `3.0 s` | How often posture is evaluated |
| `NOTIFICATION_COOLDOWN` | `60.0 s` | Minimum gap between alerts |
| `SHOULDER_TILT_TOLERANCE` | `0.025` | Sensitivity to uneven shoulders |
| `EAR_TILT_TOLERANCE` | `0.025` | Sensitivity to head tilt |
| `NECK_GAP_TOLERANCE` | `0.03` | Sensitivity to hunching |
| `HEAD_DROP_TOLERANCE` | `0.02` | Sensitivity to looking down |

Smaller values = more sensitive. Calibrating first is strongly recommended.

---

## Requirements

- macOS 12+
- Built-in or external webcam
- Python 3.10+
