from actionpack import Action
from actionpack.action import K
from tests.actionpack import FakeFile

from requests import Response
from time import sleep


class FakeResponse(Response):
    def __init__(self, content: bytes = bytes(), status: int = 200):
        self._content = content
        self.status_code = status


class FakeWriteBytes(Action[int, K]):
    def __init__(self, file: FakeFile, bytes_to_write: bytes, delay: float):
        self.bytes_to_write = bytes_to_write
        self.delay = delay
        self.file = file

    def instruction(self) -> int:
        sleep(self.delay)
        result = self.file.write(self.bytes_to_write)
        return result
