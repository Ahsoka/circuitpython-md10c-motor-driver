import microcontroller
import digitalio
import pwmio

# Inspired by adafruit_motor.motor library
# https://docs.circuitpython.org/projects/motor/en/latest/index.html

try:
    import typing
except ImportError:
    pass


class Motor:
    """DC motor driver for MD10C"""

    def __init__(
        self,
        pwm: typing.Union[pwmio.PWMOut, microcontroller.Pin],
        dir: typing.Union[digitalio.DigitalInOut, microcontroller.Pin]
    ):
        if isinstance(pwm, microcontroller.Pin):
            # TODO: Maybe i should think more carefully about this frequency, kinda just using whatever atm lol
            pwm = pwmio.PWMOut(pwm, frequency=5_000)
        if not isinstance(pwm, pwmio.PWMOut):
            raise TypeError(
                f"pwm argument must be microcontroller.Pin or pwmio.PWMOut, not {type(dir)!r}"
            )
        self.pwm = pwm

        if isinstance(dir, microcontroller.Pin):
            dir = digitalio.DigitalInOut(dir)
            dir.direction = digitalio.Direction.OUTPUT
        elif isinstance(dir, digitalio.DigitalInOut):
            if dir.direction != digitalio.Direction.OUTPUT:
                raise ValueError(
                    "dir must be have a direction set to digitalio.Direction.OUTPUT, "
                    + f"its current direction is to {digitalio.Direction.OUTPUT!r}"
                )
        else:
            raise TypeError(
                f"dir argument must be microcontroller.Pin or digitalio.DigitalInOut, not {type(dir)!r}"
            )

        self.dir = dir
        self._throttle = None

    @property
    def throttle(self) -> float:
        """Motor speed, ranging from -1.0 (full speed reverse) to 1.0 (full speed forward),
        or ``None`` (controller off).
        If ``None``, both PWMs are turned full off. If ``0.0``, both PWMs are turned full on.
        """
        return self._throttle

    @throttle.setter
    def throttle(self, value: float):
        if value is not None and (value > 1.0 or value < -1.0):
            raise ValueError("Throttle must be None or between -1.0 and +1.0")
        self._throttle = value
        if value is None:
            value = 0
        self.dir.value = value < 0
        self.pwm.duty_cycle = int(0xFFFF * abs(value))

    def __enter__(self) -> "DCMotor":
        return self

    def __exit__(
        self,
        exception_type,
        exception_value,
        traceback,
    ) -> None:
        self.throttle = None
        self.dir.deinit()
        self.pwm.deinit()
