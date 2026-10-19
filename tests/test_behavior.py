import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'firmware'))
from hardware.doors import ReedDoor
from hardware.lights import Led
from appliances.timed_light import TimedLight
from kitchen import Kitchen


def ns(seconds):
    return int(seconds * 1_000_000_000)


class Pin:
    def __init__(self, value=True):
        self.value = value


class Pwm:
    duty_cycle = 0


class BehaviorTests(unittest.TestCase):
    def make_kitchen(self, closed=False):
        pin = Pin(not closed)
        pwm = Pwm()
        appliance = TimedLight(Led(pwm))
        return pin, pwm, appliance, Kitchen(ReedDoor(pin, 0), appliance)

    def test_startup_closed_does_not_start(self):
        pin, pwm, appliance, kitchen = self.make_kitchen(closed=True)
        kitchen.update(ns(20))
        self.assertEqual(pwm.duty_cycle, 0)
        self.assertEqual(appliance.state, 'idle')

    def test_bounce_hold_fade_and_no_retrigger(self):
        pin, pwm, appliance, kitchen = self.make_kitchen()
        pin.value = False
        kitchen.update(ns(1))
        pin.value = True
        kitchen.update(ns(1.02))
        kitchen.update(ns(1.1))
        self.assertEqual(pwm.duty_cycle, 0)
        pin.value = False
        kitchen.update(ns(2))
        kitchen.update(ns(2.039))
        self.assertEqual(pwm.duty_cycle, 0)
        kitchen.update(ns(2.04))
        maximum = int(65535 * .35)
        self.assertEqual(pwm.duty_cycle, maximum)
        kitchen.update(ns(10.54))
        self.assertEqual(appliance.state, 'fading')
        self.assertAlmostEqual(pwm.duty_cycle, maximum / 2, delta=1)
        kitchen.update(ns(11.04))
        self.assertEqual(pwm.duty_cycle, 0)
        kitchen.update(ns(100))
        self.assertEqual(pwm.duty_cycle, 0)

    def test_open_cancels_and_reclose_restarts(self):
        pin, pwm, appliance, kitchen = self.make_kitchen()
        pin.value = False
        kitchen.update(ns(1))
        kitchen.update(ns(1.04))
        pin.value = True
        kitchen.update(ns(2))
        kitchen.update(ns(2.04))
        self.assertEqual(pwm.duty_cycle, 0)
        pin.value = False
        kitchen.update(ns(3))
        kitchen.update(ns(3.04))
        kitchen.update(ns(10))
        self.assertEqual(appliance.state, 'on')
        self.assertGreater(pwm.duty_cycle, 0)

    def test_independent_timers_and_long_uptime(self):
        first, second = Pwm(), Pwm()
        a, b = TimedLight(Led(first)), TimedLight(Led(second))
        origin = ns(90 * 24 * 3600)
        a.start(origin)
        b.start(origin + ns(5))
        a.update(origin + ns(9))
        b.update(origin + ns(9))
        self.assertEqual(first.duty_cycle, 0)
        self.assertGreater(second.duty_cycle, 0)
        pin = Pin()
        door = ReedDoor(pin, origin)
        pin.value = False
        door.update(origin)
        self.assertIsNone(door.update(origin + ns(.039)))
        self.assertEqual(door.update(origin + ns(.040)), 'closed')

    def test_brightness_cap_and_zero_fade(self):
        pwm = Pwm()
        light = Led(pwm)
        light.set_level(2)
        self.assertEqual(pwm.duty_cycle, int(65535 * .35))
        light.set_level(-1)
        self.assertEqual(pwm.duty_cycle, 0)
        appliance = TimedLight(light, fade_seconds=0)
        appliance.start(0)
        appliance.update(ns(8))
        self.assertEqual(pwm.duty_cycle, 0)


if __name__ == '__main__':
    unittest.main()
