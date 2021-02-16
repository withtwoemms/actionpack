from actionpack.utils import synchronized

from oslash import Left
from oslash import Right
from threading import RLock
from typing import List
from typing import Union


class Action:

    lock = RLock()

    @synchronized(lock)
    def perform(self, should_raise: bool=False) -> Union[Left, Right]:
        if callable(self.instruction):
            try:
                return Right(self.validate().instruction())
            except Exception as e:
                if should_raise:
                    raise e
                return Left(e)
        else:
            return Left(TypeError(f'Must be callable: {self.instruction}'))

    def validate(self):
        return self

    def _name(self, _name):
        self.name = _name

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise self.__class__.NotComparable(f'{str(self)} ≠ {str(other)}')

        return self.__getstate__() == other.__getstate__()

    def __repr__(self):
        return f'{self.__class__.__name__}'

    class NotComparable(Exception): pass

