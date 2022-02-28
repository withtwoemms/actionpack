from __future__ import annotations
from pathlib import Path
from re import finditer
from typing import Union

from actionpack import Action
from actionpack.action import Name


FileContents = Union[bytes, str]


class Remove(Action[Name, FileContents]):

    def __init__(self, filename: str, tail: bool = False):
        self.path = Path(filename)
        self.tail = tail

    def instruction(self) -> FileContents:
        # (line.group(0) for line in finditer(r'\w.+', self.path.read_text()))
        with open(str(self.path), 'r+') as file:
            lines = file.readlines()
            to_remove = lines.pop(-1) if self.tail else lines.pop(0)
            file.seek(0)
            for line in lines:
                file.write(line)
            file.truncate()
        return to_remove
        # return to_remove.decode('') if self.output_type is str else to_remove.encode()
        # return self.path.read_bytes() if self.output_type is bytes else self.path.read_text()

    def validate(self) -> Remove[Name, FileContents]:
        if not self.path.exists():
            raise FileNotFoundError(str(self.path))
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
