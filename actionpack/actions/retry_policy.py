from __future__ import annotations

import math
import random

from enum import Enum
from string import Template
from time import sleep

from actionpack import Action
from actionpack.action import Result
from actionpack.action import Name
from actionpack.action import Outcome
from actionpack.utils import tally


class RetryPolicy(Action[Name, Outcome]):
    def __init__(
        self,
        action: Action[Name, Outcome],
        max_retries: int,
        delay_between_attempts: int = 0,
        max_delay: int = 3600,
        backoff: str = 'CONSTANT',
        jitter_percentage: float = 1.0,
        should_record: bool = False
    ):
        if not isinstance(max_retries, int) or max_retries < 0:
            raise self.Invalid(f'The number of max_retries must be greater than zero. Given max_retries={max_retries}.')
        if jitter_percentage not in range(101):
            raise self.Invalid(f'The number of max_retries must be greater than zero. Given max_retries={max_retries}.')

        self.action = action
        self.backoff = RetryPolicy.Backoff(backoff)
        self.delay_between_attempts = delay_between_attempts
        self.jitter_percentage = jitter_percentage
        self.max_delay = max_delay
        self.max_retries = max_retries
        self.should_record = should_record

        if self.should_record:
            self.attempts: list[Result[Outcome]] = []

    def instruction(self) -> Outcome:
        return self.enact()

    def validate(self) -> RetryPolicy:
        if self.expired:
            raise RetryPolicy.Expired(f'Gave up on {str(self.action)} after {self.max_retries + 1} attempts.')
        if self.enacted:
            raise RetryPolicy.Enacted(f'{str(self.action)} already attempted. Will not perform.')
        return self

    @property
    def retries(self) -> int:
        try:
            return self._retries
        except AttributeError:
            pass
        return -1

    @property
    def enacted(self):
        return self.retries >= 0

    @property
    def expired(self):
        return self.retries >= self.max_retries

    def enact(self, counter: int = -1) -> Outcome:
        if not isinstance(counter, int) or counter < -1:
            raise self.Invalid(f'Cannot proceed with given `counter` param value: {counter}.')

        for _tally in tally(1 + self.max_retries):
            if self.expired:
                break  # pragma: no cover
            attempt = self.action.perform()
            counter += _tally
            with_delay = self.backoff.calculate(
                counter, self.delay_between_attempts, self.jitter_percentage
            )
            self._retries = counter
            if self.should_record:
                self.attempts.append(attempt)
            if attempt.successful:
                return attempt.value
            sleep(with_delay)

        raise RetryPolicy.Expired(f'Max retries exceeded: {self.max_retries}.')

    def __repr__(self):
        tmpl = Template('<$class_name($total_attempts x $action_name$delay)>')
        return tmpl.substitute(
            class_name=self.__class__.__name__,
            total_attempts=self.max_retries + 1,
            action_name=str(self.action),
            delay='' if not self.delay_between_attempts else f' | {self.delay_between_attempts}s delay'
        )

    class Expired(Exception):
        pass

    class Enacted(Exception):
        pass

    class Backoff(Enum):
        CONSTANT = 'CONSTANT'
        LINEAR = 'LINEAR'
        EXPONENTIAL = 'EXPONENTIAL'

        def calculate(self, coefficient: float, base: int, jitter_percentage: float):
            if base == 0:
                return 0
            factor, is_fraction = self._rectify(base)
            base = abs(factor * base if is_fraction else base)
            coefficient = abs(coefficient)

            approaches = {
                self.CONSTANT: (coefficient ** 0) * base,       # 2, 2, 2, 2, ...
                self.LINEAR: ((coefficient + 1) ** 1) * base,   # 2, 4, 6, 8, ...
                self.EXPONENTIAL: (base ** coefficient) * base  # 2, 4, 8, 16, ...
            }
            delay = approaches[self] / factor if is_fraction else approaches[self]
            jitter_fraction = (jitter_percentage / 100) * base
            jitter = random.uniform(-jitter_fraction, jitter_fraction)
            return delay + jitter

        def _rectify(self, base: float):
            order_of_magnitude = math.floor(math.log(abs(base), 10))
            is_fraction = order_of_magnitude < 1
            if is_fraction:
                factor = 1 * 10 ** (abs(order_of_magnitude))
            else:
                factor = 1
            return factor, is_fraction
