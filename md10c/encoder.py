from .motor import Motor

import microcontroller
import digitalio
import rotaryio
import pwmio
import time
import math

try:
    import typing
except ImportError:
    pass

tau = 2 * math.pi # NOTE: https://www.youtube.com/watch?v=bcPTiiiYDs8


class MotorEncoder(Motor):
    def __init__(
        self,
        pwm: typing.Union[pwmio.PWMOut, microcontroller.Pin],
        dir: typing.Union[digitalio.DigitalInOut, microcontroller.Pin],
        channel_a: microcontroller.Pin,
        channel_b: microcontroller.Pin,
        rotations: int,
        divisor: int = 1
    ):
        super().__init__(pwm, dir)

        self.encoder = rotaryio.IncrementalEncoder(channel_a, channel_b, divisor=divisor)
        # NOTE: This value is the "Encoder: Countable Events Per Revolution (Output Shaft)" for ServoCity motors
        self.rotations = rotations

    @property
    def position(self):
        return self.encoder.position

    @property
    def radians(self) -> float:
        return tau * self.position / self.rotations

    @property
    def degrees(self) -> float:
        return math.degrees(self.radians)

    @property
    def rpm(self) -> float:
        last_pos = self.position
        delay = 0.01
        time.sleep(delay)
        return 60 * (self.position - last_pos) / delay / self.rotations

    @property
    def radians_per_second(self) -> float:
        return self.rpm / 60 * tau

    def __exit__(self, exception_type, exception_value, traceback):
        super().__exit__(exception_type, exception_value, traceback)
        self.encoder.deinit()
