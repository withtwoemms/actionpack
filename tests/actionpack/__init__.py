from io import BytesIO
from io import StringIO
from typing import Callable

from actionpack import Action
from actionpack.action import Name
from actionpack.action import Outcome


class FakeAction(Action[Name, Outcome]):

    result = 'Performing Action.'

    def __init__(
        self,
        name: Name = None,
        instruction_provider: Callable = None,
    ):
        self.name = name
        self.instruction_provider = instruction_provider
        self.state = {'this': 'state'}

    def instruction(self) -> str:
        return self.instruction_provider() if self.instruction_provider else self.result


class FakeFile:
    def __init__(self, contents=None, mode: str = None):
        if not contents:
            contents = bytes()
        self.buffer = BytesIO(contents) if isinstance(contents, bytes) else StringIO(contents)
        self.buffer.read()
        self.mode = mode

    def read(self):
        self.buffer.seek(0)
        return self.buffer.read()

    def write(self, data):
        if self.mode in ['wb', 'w']:
            self.buffer.seek(0)
            self.buffer.truncate()
        self.buffer.write(data)
        return len(data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True
