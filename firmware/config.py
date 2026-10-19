"""Prototype wiring; GP15 will need reassignment for the second door later."""
import board

REED_PIN = board.GP14
LED_PIN = board.GP15
DEBOUNCE_SECONDS = 0.04
HOLD_SECONDS = 8.0
FADE_SECONDS = 1.0
MAX_BRIGHTNESS = 0.35
PWM_FREQUENCY = 1000
