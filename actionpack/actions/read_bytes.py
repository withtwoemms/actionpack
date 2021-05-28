from __future__ import annotations
from pathlib import Path

from actionpack import Action
from actionpack.action import Name


class ReadBytes(Action[bytes, Name]):
    def __init__(self, filename: str):
        self.path = Path(filename)

    def instruction(self) -> bytes:
        return self.path.read_bytes()

    def validate(self) -> ReadBytes[bytes, Name]:
        if not self.path.exists():
            raise FileNotFoundError(str(self.path))
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
