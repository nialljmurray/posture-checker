from dataclasses import dataclass, field
from typing import Optional

# Landmark indices (same in both old and new MediaPipe APIs)
_NOSE          = 0
_LEFT_EAR      = 7
_RIGHT_EAR     = 8
_LEFT_SHOULDER = 11
_RIGHT_SHOULDER = 12


@dataclass
class PostureReport:
    is_good: bool
    shoulder_tilt: float
    ear_tilt: float
    neck_gap: float
    head_drop: float
    issues: list[str] = field(default_factory=list)


@dataclass
class _Baseline:
    shoulder_tilt: float
    ear_tilt: float
    neck_gap: float
    head_drop: float


class PostureAnalyzer:
    def __init__(
        self,
        shoulder_tilt_tolerance: float,
        ear_tilt_tolerance: float,
        neck_gap_tolerance: float,
        head_drop_tolerance: float,
    ):
        self._shoulder_tilt_tolerance = shoulder_tilt_tolerance
        self._ear_tilt_tolerance = ear_tilt_tolerance
        self._neck_gap_tolerance = neck_gap_tolerance
        self._head_drop_tolerance = head_drop_tolerance
        self._baseline: Optional[_Baseline] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calibrate(self, pose_landmarks_list) -> bool:
        """Record the current pose as the good-posture baseline.
        Returns True on success, False if landmarks were not visible."""
        metrics = self._compute_metrics(pose_landmarks_list)
        if metrics is None:
            return False
        self._baseline = _Baseline(*metrics)
        return True

    def analyze(self, pose_landmarks_list) -> Optional[PostureReport]:
        """Return a PostureReport, or None if landmarks are not visible."""
        metrics = self._compute_metrics(pose_landmarks_list)
        if metrics is None:
            return None

        shoulder_tilt, ear_tilt, neck_gap, head_drop = metrics
        issues: list[str] = []

        if self._baseline:
            if shoulder_tilt - self._baseline.shoulder_tilt > self._shoulder_tilt_tolerance:
                issues.append("Uneven shoulders — adjust your seating")
            if ear_tilt - self._baseline.ear_tilt > self._ear_tilt_tolerance:
                issues.append("Head tilted — straighten your neck")
            if self._baseline.neck_gap - neck_gap > self._neck_gap_tolerance:
                issues.append("Hunching — sit up and roll shoulders back")
            if self._baseline.head_drop - head_drop > self._head_drop_tolerance:
                issues.append("Head dropped — raise your screen or sit up")
        else:
            # Pre-calibration: absolute checks only (neck gap and head drop
            # need a personal baseline to be meaningful, skip them here)
            if shoulder_tilt > self._shoulder_tilt_tolerance:
                issues.append("Uneven shoulders — adjust your seating")
            if ear_tilt > self._ear_tilt_tolerance:
                issues.append("Head tilted — straighten your neck")

        return PostureReport(
            is_good=len(issues) == 0,
            shoulder_tilt=shoulder_tilt,
            ear_tilt=ear_tilt,
            neck_gap=neck_gap,
            head_drop=head_drop,
            issues=issues,
        )

    @property
    def is_calibrated(self) -> bool:
        return self._baseline is not None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _compute_metrics(self, pose_landmarks_list) -> Optional[tuple[float, float, float, float]]:
        if not pose_landmarks_list:
            return None

        lm = pose_landmarks_list[0]  # first (and typically only) person

        nose = lm[_NOSE]
        ls   = lm[_LEFT_SHOULDER]
        rs   = lm[_RIGHT_SHOULDER]
        le   = lm[_LEFT_EAR]
        re   = lm[_RIGHT_EAR]

        if any(pt.visibility < 0.5 for pt in (ls, rs, le, re)):
            return None

        shoulder_tilt = abs(ls.y - rs.y)
        ear_tilt      = abs(le.y - re.y)

        shoulder_mid_y = (ls.y + rs.y) / 2
        ear_mid_y      = (le.y + re.y) / 2

        # Positive when ears are above shoulders — shrinks when hunching
        neck_gap  = shoulder_mid_y - ear_mid_y
        # Positive when nose is above shoulder midpoint — shrinks when head drops
        head_drop = shoulder_mid_y - nose.y

        return shoulder_tilt, ear_tilt, neck_gap, head_drop
