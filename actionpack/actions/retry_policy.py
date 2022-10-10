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
        self.action = action
        self.max_retries = max_retries
        self.delay_between_attempts = delay_between_attempts
        self.should_record = should_record

        if self.should_record:
            self.attempts: list[Result[Outcome]] = []

    def instruction(self) -> Outcome:
        return self.enact(self.delay_between_attempts)

    def validate(self) -> RetryPolicy:
        try:
            if self.retries >= 0:
                raise RetryPolicy.Expired(f'{str(self.action)} already attempted. Will not perform.')
        except AttributeError:
            pass
        finally:
            return self

    def enact(self, with_delay: int = 0, counter: int = -1) -> Outcome:
        for _tally in tally(1 + self.max_retries):
            sleep(with_delay)
            counter += _tally
            self.retries = counter
            retry = self.action.perform()
            if self.should_record:
                self.attempts.append(retry)
            if retry.successful:
                return retry.value

        raise RetryPolicy.Expired(f'Max retries exceeded: {self.max_retries}.')

    def __repr__(self):
        tmpl = Template('<$class_name($max_retries x $action_name$delay)>')
        return tmpl.substitute(
            class_name=self.__class__.__name__,
            max_retries=self.max_retries,
            action_name=str(self.action),
            delay='' if not self.delay_between_attempts else f' | {self.delay_between_attempts}s delay'
        )

    class Expired(Exception):
        pass
