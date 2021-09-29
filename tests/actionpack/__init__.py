from io import BytesIO
from io import StringIO

from actionpack import Action
from actionpack.action import Name
from actionpack.action import Outcome


class FakeAction(Action[Name, Outcome]):

    result = 'Performing Action.'

    def __init__(self, name: Name = None, exception=None):
        self.name = name
        self.exception = exception
        self.state = {'this': 'state'}

    def instruction(self) -> str:
        return self.result

    def validate(self):
        if self.exception:
            raise self.exception
        return super().validate()


class FakeFile:
    def __init__(self, contents: bytes = bytes(), mode: str = None):
        self.buffer = BytesIO(contents) if mode not in ['a', 'a+'] else StringIO(contents.decode())
        self.buffer.read()
        self.mode = mode

    def read(self):
        self.buffer.seek(0)
        return self.buffer.read()

    def write(self, data: bytes):
        if self.mode == 'wb':
            self.buffer.seek(0)
            self.buffer.truncate()
        self.buffer.write(data)
        return len(data)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True
