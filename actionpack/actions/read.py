from __future__ import annotations
from pathlib import Path

from actionpack import Action
from actionpack.action import Name


class Read(Action[Name, bytes]):
    def __init__(self, filename: str, output_type: type = str):
        if output_type not in [bytes, str]:
            raise TypeError(f'Must be of type bytes or str: {output_type}')
        self.output_type = output_type
        self.path = Path(filename)

    def instruction(self) -> bytes:
        return self.path.read_bytes() if self.output_type is bytes else self.path.read_text()

    def validate(self) -> Read[Name, bytes]:
        if not self.path.exists():
            raise FileNotFoundError(str(self.path))
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
