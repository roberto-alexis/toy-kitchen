"""Active-low reed input with stable-state debounce and edge events."""


class ReedDoor:
    def __init__(self, input_pin, now, debounce_seconds=0.04):
        self._input = input_pin
        self._debounce = debounce_seconds
        self._candidate = not input_pin.value
        self.is_closed = self._candidate
        self._changed_at = now

    def update(self, now):
        """Return 'closed', 'opened', or None; startup produces no event."""
        raw_closed = not self._input.value
        if raw_closed != self._candidate:
            self._candidate = raw_closed
            self._changed_at = now
        if (self._candidate != self.is_closed
                and (now - self._changed_at) / 1_000_000_000 >= self._debounce):
            self.is_closed = self._candidate
            return "closed" if self.is_closed else "opened"
        return None
