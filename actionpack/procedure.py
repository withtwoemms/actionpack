from actionpack import Action

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from functools import reduce
from multiprocessing.pool import ThreadPool
from typing import List


class Procedure:
    def __init__(self, *actions: List[Action], sync: bool=True):
        self.actions = actions
        self._actions = iter(self.actions)
        self.sync = sync

    def validate(self):
        try:
            for action in self.actions:
                if not isinstance(action, Action):
                    msg = f'Procedures can only execute Actions: {str(action)}'
                    raise Procedure.NotAnAction(msg)
        except Exception as e:
            raise e

    def execute(self, max_workers: int=5):
        if self.sync:
            for action in self.actions:
                yield action.perform()
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action.perform): str(action) for action in self}
                for future in as_completed(futures):
                    yield future.result()

    def __repr__(self):
        for action in self.actions:
            header = f'\nProcedure for {"synchronously" if self.sync else "asynchronously"} performing\nthe following Actions:\n'
            bullet = '  * '
            actions = reduce(lambda a, b: str(a) + f'\n{bullet}' + str(b), self.actions)
            return header + bullet + actions

    def __iter__(self):
        return self._actions

    def __next__(self):
        try:
            return next(self._actions)
        except StopIteration:
            self._actions = iter(self.actions)

    class NotAnAction(Exception): pass


class KeyedProcedure(Procedure):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validate()

    def validate(self):
        for action in self.actions:
            if not action.__dict__.get('name'):
                msg = f'All {self.__class__.__name__} Actions must have a name: {str(action)}'
                raise KeyedProcedure.UnnamedAction(msg)

    def execute(self, max_workers: int=5):
        if self.sync:
            for action in self.actions:
                yield action.name, action.perform()
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action.perform): action for action in self}
                for future in as_completed(futures):
                    yield futures[future].name, future.result()

    class UnnamedAction(Exception): pass

