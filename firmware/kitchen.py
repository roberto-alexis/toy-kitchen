"""Route door events to an appliance without exposing GPIO polarity."""


class Kitchen:
    def __init__(self, door, appliance):
        self._door = door
        self._appliance = appliance

    def update(self, now):
        event = self._door.update(now)
        if event == "closed":
            self._appliance.start(now)
        elif event == "opened":
            self._appliance.stop()
        self._appliance.update(now)
