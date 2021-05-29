import pickle

from functools import wraps
from typing import Callable
from typing import Generic
from typing import Optional
from typing import TypeVar


T = TypeVar('T')


class Closure(Generic[T]):
    def __init__(self, func: Callable[..., T], *args, **kwargs):
        if callable(func) and func.__name__ == '<lambda>':
            raise self.LambdaNotAllowed(repr(func))
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self) -> T:
        return self.func(*self.args, **self.kwargs)

    def __repr__(self):
        return f'<{self.__class__.__name__}({self.func.__name__})|*{self.args}, **{self.kwargs}>'

    def __hash__(self):
        contents = (self.func, self.args, tuple(self.kwargs.items()))
        return hash(contents)

    def __eq__(self, other):
        return hash(self) == hash(other)

    class LambdaNotAllowed(Exception):
        pass


def tally(num=1):
    while (num if num > 0 else -1 * num) > 0:
        yield 1 if num > 0 else -1
        num = num - 1 if num > 0 else num + 1


def pickleable(obj) -> Optional[bytes]:
    try:
        return pickle.dumps(obj)
    except Exception:
        pass


def synchronized(lock):
    def wrap(f):
        @wraps(f)
        def newFunction(*args, **kw):
            with lock:
                return f(*args, **kw)
        return newFunction
    return wrap
