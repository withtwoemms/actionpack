from actionpack import Action
from actionpack.utils import tally

from oslash import Left
from oslash import Right
from string import Template
from time import sleep
from typing import Union


class RetryPolicy(Action):
    def __init__(self, action: Action, max_retries: int, delay_between_attempts: int=0):
        self.action = action
        self.max_retries = max_retries
        self.delay_between_attempts = delay_between_attempts

    def instruction(self):
        return self.enact(self.delay_between_attempts)

    def validate(self):
        try:
            if self.retries >= 0:
                raise RetryPolicy.Expired(f'{str(self.action)} already attempted. Will not perform.')
        except AttributeError:
            pass
        finally:
            return self

    def enact(self, with_delay: int=0, counter: int=0) -> Union[Left, Right]:
        result = self.action.perform()
        for _tally in tally(self.max_retries):
            if isinstance(result, Right):
                self.retries = counter
                return result
            else:
                counter += _tally
                result = self.action.perform()
                sleep(with_delay)
        self.retries = counter
        raise RetryPolicy.Expired(f'Max retries exceeded: {self.max_retries}.')

    def __repr__(self):
        tmpl = Template('$class_name($max_retries x $action_name$delay)')
        return tmpl.substitute(
            class_name=self.__class__.__name__,
            max_retries=self.max_retries,
            action_name=str(self.action),
            delay='' if not self.delay_between_attempts else f' | {self.delay_between_attempts}s delay'
        )

    class Expired(Exception): pass

