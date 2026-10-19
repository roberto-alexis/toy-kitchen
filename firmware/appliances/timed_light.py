"""Independent, non-blocking hold and fade state machine."""


class TimedLight:
    def __init__(self, light, hold_seconds=8.0, fade_seconds=1.0):
        if hold_seconds < 0 or fade_seconds < 0:
            raise ValueError("Durations cannot be negative")
        self._light = light
        self._hold = hold_seconds
        self._fade = fade_seconds
        self._started_at = None
        self.state = "idle"
        self.stop()

    def start(self, now):
        self._started_at = now
        self.state = "on"
        self._light.set_level(1)

    def stop(self):
        self._started_at = None
        self.state = "idle"
        self._light.set_level(0)

    def update(self, now):
        if self._started_at is None:
            return
        elapsed = (now - self._started_at) / 1_000_000_000
        if elapsed < self._hold:
            return
        if self._fade == 0 or elapsed >= self._hold + self._fade:
            self.stop()
        else:
            self.state = "fading"
            self._light.set_level(1 - (elapsed - self._hold) / self._fade)
