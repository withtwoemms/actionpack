from actionpack import Action
from pathlib import Path


class ReadBytes(Action):
    def __init__(self, filename: str):
        self.path = Path(filename)

    def instruction(self) -> bytes:
        return self.path.read_bytes()

    def validate(self):
        if not self.path.exists():
            raise FileNotFoundError(str(self.path))
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self

