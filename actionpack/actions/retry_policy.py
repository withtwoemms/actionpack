from __future__ import annotations
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
        should_record: bool = False
    ):
        if not isinstance(max_retries, int) or max_retries < 0:
            raise self.Invalid(f'The number of max_retries must be greater than zero. Given max_retries={max_retries}.')

        self.action = action
        self.max_retries = max_retries
        self.delay_between_attempts = delay_between_attempts
        self.should_record = should_record

        if self.should_record:
            self.attempts: list[Result[Outcome]] = []

    def instruction(self) -> Outcome:
        return self.enact(self.delay_between_attempts)

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

    def enact(self, with_delay: int = 0, counter: int = -1) -> Outcome:
        if not isinstance(counter, int) or counter < -1:
            raise self.Invalid(f'Cannot proceed with given `counter` param value: {counter}.')

        for _tally in tally(1 + self.max_retries):
            if self.expired:
                break  # pragma: no cover
            attempt = self.action.perform()
            counter += _tally
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
