from __future__ import annotations
from pathlib import Path

from actionpack import Action
from actionpack.action import K


class ReadBytes(Action[bytes, K]):
    def __init__(self, filename: str):
        self.path = Path(filename)

    def instruction(self) -> bytes:
        return self.path.read_bytes()

    def validate(self) -> ReadBytes[bytes, K]:
        if not self.path.exists():
            raise FileNotFoundError(str(self.path))
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
