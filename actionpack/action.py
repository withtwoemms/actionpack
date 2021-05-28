from __future__ import annotations
from oslash import Left
from oslash import Right
from oslash.either import Either
from string import Template
from subprocess import PIPE
from subprocess import run
from sys import executable as python
from threading import RLock
from typing import Optional
from typing import Generic
from typing import TypeVar
from typing import Union

from actionpack.utils import synchronized


T = TypeVar('T')
K = TypeVar('K')
ResultValue = Union[T, Exception]


class Result(Generic[T]):
    def __init__(self, outcome: Either):
        self.value: Optional[ResultValue[T]] = None
        if isinstance(outcome, Right):
            self.value = outcome.value
        elif isinstance(outcome, Left):
            self.value = outcome.value
        else:
            raise self.OutcomeMustBeOfTypeEither

    class OutcomeMustBeOfTypeEither:
        pass


class Action(Generic[T, K]):

    _name: Optional[K] = None

    lock = RLock()

    def _perform(self, should_raise: bool = False) -> Result[T]:
        if not callable(self.instruction):
            outcome = Left(TypeError(f'Must be callable: {self.instruction}'))
            return Result(outcome)
        try:
            outcome = Right(self.validate().instruction())
            return Result(outcome)
        except Exception as e:
            if should_raise:
                raise e
            outcome = Left(e)
            return Result(outcome)

    def __init_subclass__(cls, requires=None):
        cls.requires = requires
        if cls.requires:
            for requirement in requires:
                Action.DependencyCheck(requirement)
                setattr(cls, requirement, __import__(requirement))

    @synchronized(lock)
    def perform(self, should_raise: bool = False) -> Result[T]:
        return self._perform(should_raise)

    def validate(self):
        return self

    def set(self, **kwargs) -> Action[T, K]:
        self._name: Optional[K] = kwargs.get('name')
        return self

    @property
    def name(self) -> Optional[K]:
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

    class NotComparable(Exception):
        pass

    class DependencyCheck:
        def __init__(self, requires: str = None):
            if not requires:
                raise self.WhichPackage('do you want to check? Please specify a requires=')

            result = run([python, '-m', 'pip', 'show', requires], stdout=PIPE, stderr=PIPE)
            if result.returncode != 0:
                raise self.PackageMissing(f'so please install "{requires}" to proceed.')

        class PackageMissing(Exception):
            pass

        class WhichPackage(Exception):
            pass
