import pickle

from itertools import chain
from typing import Optional


def tally(num=1):
    while (num if num > 0 else -1 * num) > 0:
        yield 1 if num > 0 else -1
        num = num - 1 if num > 0 else num + 1


def pickleable(obj) -> Optional[bytes]:
    try:
        return pickle.dumps(obj)
    except Exception:
        pass

