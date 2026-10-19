# Toy kitchen

CircuitPython firmware for a Raspberry Pi Pico 2 / Pico 2 W. This first
prototype uses one purchased Gebildet normally open reed switch and one
ordinary two-lead LED. No third-party libraries are required.

## Behavior

- Boot: LED off, even if the magnet is already near the reed.
- Move magnet away, then near: after 40 ms of stable contact, illuminate
  for 8 seconds, then fade out over 1 second.
- Move magnet away during the cycle: turn off after the 40 ms debounce.
- Keeping the magnet near does not repeatedly trigger the timer.
- A new close transition starts a fresh cycle.

Opening cancels the cycle as a prototype default; it can be changed in
`kitchen.py`. The single LED cannot reproduce the eventual RGB colors.

## Wiring (disconnect power before changing wires)

| Connection | Pico signal | Physical header pin |
| --- | --- | --- |
| Reed lead 1 | GP14 | 19 |
| Reed lead 2 | GND | 18 (or another GND) |
| LED anode through a 330 ohm series resistor | GP15 | 20 |
| LED cathode | GND | 18 (or another GND) |

The resistor and LED are in series: GP15 -> resistor -> LED anode;
LED cathode -> GND. Use an ordinary small indicator LED. PWM limits average
brightness to 35%, but does not replace the current-limiting resistor.
The reed has no polarity. Verify that magnet-near closes its contacts.
The software enables the internal pull-up: closed reads low, open reads high.
Never connect 5 V to either GPIO. For this prototype, power the Pico via
its laptop USB connection; external power is not required.

GP15 is temporarily used for the prototype LED. The larger kitchen plan
reserves it for the microwave reed, so reassign it when expanding.
Secure magnets out of children's reach before installing in the toy.

## Install

Use CircuitPython firmware for your exact board (Pico 2 W if that is the
board you are using). This code targets CircuitPython 10.x built-in APIs.
Physical testing and the exact installed firmware version are still pending.

1. Back up the existing contents of the mounted `CIRCUITPY` drive.
2. Copy the **contents** of `firmware/` to the root of `CIRCUITPY`.
   `code.py` must be at its root, not inside a `firmware` directory.
3. Wait for copying to finish, then press Ctrl+D in the CircuitPython serial
   console to reload. Saving files may also cause automatic reloads.
4. Move the magnet away and back. Check the behavior above.

On macOS, from the repository directory:

```sh
cp -R firmware/. /Volumes/CIRCUITPY/
```

This overwrites matching runtime files; it does not delete unrelated files.
Do not copy tests, Git files, or the README onto the board.

## Organization

| Path | Responsibility |
| --- | --- |
| `firmware/code.py` | Hardware setup, cleanup, shared update loop |
| `firmware/config.py` | Pin assignments, debounce, durations, brightness |
| `firmware/hardware/doors.py` | Debounced reed state and transition events |
| `firmware/hardware/lights.py` | PWM brightness adapter |
| `firmware/appliances/timed_light.py` | Independent hold/fade state machine |
| `firmware/kitchen.py` | Route door events to the light controller |
| `tests/test_behavior.py` | Laptop tests with fake hardware and clock |

Timestamps passed to constructors/update/start are integer nanoseconds.
Durations in configuration are seconds. Elapsed differences are converted
only after subtraction, preserving debounce precision during long uptimes.
There are no blocking waits in appliance logic. A second appliance can use
another instance with its own timer. Exceptions shut the LED off and remain
visible in the serial console; the code does not silently restart.

## Laptop verification

```sh
python3 -m unittest discover -s tests -v
```

Tests do not require CircuitPython packages on your laptop. They verify logic
with fake inputs/outputs; actual GPIO, PWM, wiring and magnet alignment must
still be verified on the Pico.

API references:
- https://docs.circuitpython.org/en/stable/shared-bindings/digitalio/
- https://docs.circuitpython.org/en/stable/shared-bindings/pwmio/
- https://docs.circuitpython.org/en/stable/shared-bindings/time/
