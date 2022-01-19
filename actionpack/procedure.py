from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from functools import reduce
from itertools import islice
from itertools import tee
from typing import Generic
from typing import Iterator
from typing import Iterable
from typing import Tuple

from actionpack.action import Name
from actionpack.action import Outcome
from actionpack.action import Result
from actionpack import Action


class Procedure(Generic[Name, Outcome]):
    def __init__(self, actions: Iterable[Action[Name, Outcome]]):
        if not (isinstance(actions, Iterator) or isinstance(actions, Iterable)):
            raise TypeError(f'Actions must be iterable. Received {type(actions)}.')

        self.actions, self._actions, self.__actions = tee(actions, 3)

    def validate(self):
        actions, spare = tee(self.__actions, 2)
        self.__actions = spare
        try:
            for action in actions:
                if not isinstance(action, Action):
                    msg = f'Procedures can only execute Actions: {str(action)}'
                    raise Procedure.NotAnAction(msg)
        except Exception as e:
            raise e

    def execute(
        self,
        max_workers: int = 5,
        should_raise: bool = False,
        synchronously: bool = True
    ) -> Iterator[Result[Outcome]]:
        if synchronously:
            for action in self:
                yield action.perform(should_raise=should_raise) if should_raise else action.perform()
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action._perform, should_raise=should_raise): str(action) for action in self}
                for future in as_completed(futures):
                    yield future.result()

    def __repr__(self):
        header = '\nProcedure for performing the following Actions:\n'
        bullet = '  * '
        actions = reduce(lambda a, b: str(a) + f'\n{bullet}' + str(b), self.actions)
        return header + bullet + str(actions)

    def __iter__(self):
        return self._actions

    def __next__(self):
        try:
            return next(self._actions)
        except StopIteration:
            return None

    class NotAnAction(Exception):
        pass


class KeyedProcedure(Procedure[Name, Outcome]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        actions = list(args)[0]
        self.actions, self._actions, self.__actions = tee(actions, 3)

        self.validate()

    def validate(self):
        actions, spare = tee(self.__actions, 2)
        self.__actions = spare
        for action in actions:
            if action.name is None:
                msg = f'All {self.__class__.__name__} Actions must have a name: {str(action)}'
                raise KeyedProcedure.UnnamedAction(msg)

    def execute(
        self,
        max_workers: int = 5,
        should_raise: bool = False,
        synchronously: bool = True
    ) -> Iterator[Tuple[Name, Result[Outcome]]]:
        if synchronously:
            for action in self:
                yield (action.name, action.perform(should_raise=should_raise)) \
                      if should_raise else (action.name, action.perform())
        else:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(action._perform, should_raise=should_raise): action for action in self}
                for future in as_completed(futures):
                    yield (futures[future].name, future.result())

    class UnnamedAction(Exception):
        pass
