from actionpack.utils import synchronized

from oslash import Left
from oslash import Right
from string import Template
from threading import RLock
from typing import List
from typing import Union


class Action:

    _name = None

    lock = RLock()

    def _perform(self, should_raise: bool=False) -> Union[Left, Right]:
        if not callable(self.instruction):
            return Left(TypeError(f'Must be callable: {self.instruction}'))

        try:
            return Right(self.validate().instruction())
        except Exception as e:
            if should_raise:
                raise e
            return Left(e)

    @synchronized(lock)
    def perform(self, should_raise: bool=False):
        return self._perform(should_raise)

    def validate(self):
        return self

    def set(self, **kwargs) -> 'Action':
        self._name = kwargs.get('name')
        return self

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        del self._name

    def __getstate__(self):
        return vars(self)

    def __setstate__(self, state):
        self.__dict__.update(state)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise self.__class__.NotComparable(f'{str(self)} ≠ {str(other)}')

        return self.__getstate__() == other.__getstate__()

    def __repr__(self):
        tmpl = Template(f'<{self.__class__.__name__}$name>')
        return tmpl.substitute(name=f'|name="{self.name}"') if self.name else tmpl.substitute(name='')

    class NotComparable(Exception): pass

