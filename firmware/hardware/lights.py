"""Standard single LED driven by PWM (not a NeoPixel driver)."""


class Led:
    def __init__(self, pwm, max_brightness=0.35):
        if not 0 <= max_brightness <= 1:
            raise ValueError("Brightness must be between zero and one")
        self._pwm = pwm
        self._maximum = max_brightness
        self.set_level(0)

    def set_level(self, level):
        """Accept a normalized level; cap the physical output centrally."""
        level = max(0.0, min(1.0, level))
        self._pwm.duty_cycle = int(65535 * self._maximum * level)
