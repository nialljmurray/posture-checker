import subprocess
import time


class Notifier:
    def __init__(self, cooldown: float):
        self._cooldown = cooldown
        self._last_sent: float = 0.0

    def notify(self, issues: list[str]) -> None:
        """Send a macOS notification if the cooldown has elapsed."""
        if time.time() - self._last_sent < self._cooldown:
            return

        body = " · ".join(issues)
        self._send("Posture Check", body)
        self._last_sent = time.time()

    @staticmethod
    def _send(title: str, message: str) -> None:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(["osascript", "-e", script], check=False)
