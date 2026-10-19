"""Copy firmware contents to CIRCUITPY; this file runs at startup."""
import time
import digitalio
import pwmio
import config
from hardware.doors import ReedDoor
from hardware.lights import Led
from appliances.timed_light import TimedLight
from kitchen import Kitchen


def clock():
    # Keep timestamps as integers; convert only elapsed intervals to seconds.
    return time.monotonic_ns()


def main():
    with pwmio.PWMOut(config.LED_PIN, frequency=config.PWM_FREQUENCY,
                     duty_cycle=0) as pwm:
        light = Led(pwm, config.MAX_BRIGHTNESS)
        try:
            with digitalio.DigitalInOut(config.REED_PIN) as pin:
                pin.switch_to_input(pull=digitalio.Pull.UP)
                door = ReedDoor(pin, clock(), config.DEBOUNCE_SECONDS)
                appliance = TimedLight(light, config.HOLD_SECONDS,
                                       config.FADE_SECONDS)
                kitchen = Kitchen(door, appliance)
                print("Ready: move magnet away, then near reed to start light.")
                while True:
                    kitchen.update(clock())
        finally:
            light.set_level(0)


main()
