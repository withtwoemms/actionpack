from actionpack import Action

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from functools import reduce
from multiprocessing.pool import ThreadPool


class Procedure:
    def __init__(self, *actions: Action):
        self.actions = actions
        self._actions = iter(self.actions)

    def validate(self):
        try:
            for action in self.actions:
                if not isinstance(action, Action):
                    msg = f'Procedures can only execute Actions: {str(action)}'
                    raise Procedure.NotAnAction(msg)
        except Exception as e:
            raise e

    def execute(self, max_workers: int=5, should_raise: bool=False, synchronously: bool=True):
        if synchronously:
            for action in self.actions:
                yield action.perform(should_raise=should_raise) if should_raise else action.perform()
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action._perform, should_raise=should_raise): str(action) for action in self}
                for future in as_completed(futures):
                    yield future.result()

    def __repr__(self):
        for action in self.actions:
            header = f'\nProcedure for performing the following Actions:\n'
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
            if action.name is None:
                msg = f'All {self.__class__.__name__} Actions must have a name: {str(action)}'
                raise KeyedProcedure.UnnamedAction(msg)

    def execute(self, max_workers: int=5, should_raise: bool=False, synchronously: bool=True):
        if synchronously:
            for action in self.actions:
                yield (action.name, action.perform(should_raise=should_raise)) \
                      if should_raise else (action.name, action.perform())
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action._perform, should_raise=should_raise): action for action in self}
                for future in as_completed(futures):
                    yield (futures[future].name, future.result())

    class UnnamedAction(Exception): pass
