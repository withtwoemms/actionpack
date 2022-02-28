from contextlib import contextmanager
from io import IOBase as Buffer
from requests import Response
from time import sleep

from actionpack import Action
from actionpack.action import Name
from tests.actionpack import FakeFile


@contextmanager
def uncloseable(buffer: Buffer):
    """
    Context manager which turns the fd's close operation to no-op for the duration of the context.
    """
    close = buffer.close
    buffer.close = lambda: None
    yield buffer
    buffer.close = close
    buffer.seek(0)  # fake close


class FakeResponse(Response):
    def __init__(self, content: bytes = bytes(), status: int = 200):
        self._content = content
        self.status_code = status


class FakeWrite(Action[Name, int]):
    def __init__(self, file: FakeFile, to_write: bytes, delay: float):
        self.to_write = to_write
        self.delay = delay
        self.file = file

    def instruction(self) -> int:
        sleep(self.delay)
        result = self.file.write(self.to_write)
        return result
