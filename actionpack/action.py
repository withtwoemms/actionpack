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


Outcome = TypeVar('Outcome')
Name = TypeVar('Name')
ResultValue = Union[Outcome, Exception]


class Result(Generic[Outcome]):

    _immutables = ('successful',)

    def __init__(self, outcome: Either):
        self.value: Optional[ResultValue[Outcome]] = None
        if type(outcome) in [Left, Right]:
            self.value = outcome.value
            self.successful = True if isinstance(outcome, Right) else False
        else:
            raise self.OutcomeMustBeOfTypeEither

    def __setattr__(self, name, value):
        if name in self._immutables and getattr(self, name, None) is not None:
            raise AttributeError(f'Cannot modify `{name}`')
        else:
            return super(Result, self).__setattr__(name, value)

    def __delattr__(self, name):
        if name in self._immutables:
            raise AttributeError(f'Cannot modify `{name}`')
        else:
            return super(Result, self).__delattr__(name)

    class OutcomeMustBeOfTypeEither(Exception):
        pass


class Action(Generic[Name, Outcome]):

    _name: Optional[Name] = None

    lock = RLock()
    requirements = tuple()

    def instruction(self):
        pass

    @synchronized(lock)
    def perform(self, should_raise: bool = False) -> Result[Outcome]:
        return self._perform(should_raise)

    def validate(self):
        return self

    def set(self, **kwargs) -> Action[Name, Outcome]:
        self._name: Optional[Name] = kwargs.get('name')
        return self

    @property
    def name(self) -> Optional[Name]:
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        del self._name

    def check_dependencies(self, cls):
        for requirement in cls.requirements:
            if not hasattr(cls, requirement):
                Action.DependencyCheck(cls, requirement)

    def _perform(self, should_raise: bool = False) -> Result[Outcome]:
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
        if requires:
            cls.requirements += requires

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
        def __init__(self, cls, requirement: str = None):
            if not requirement:
                raise self.WhichPackage('do you want to check? Please specify a requirment kwarg.')

            result = run([python, '-m', 'pip', 'show', requirement], stdout=PIPE, stderr=PIPE)
            if result.returncode != 0:
                raise self.PackageMissing(f'so please install "{requirement}" to proceed.')

            setattr(cls, requirement, __import__(requirement))

        class PackageMissing(Exception):
            pass

        class WhichPackage(Exception):
            pass
