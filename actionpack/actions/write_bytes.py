from __future__ import annotations
from pathlib import Path

from actionpack import Action
from actionpack.action import Name


class WriteBytes(Action[Name, int]):
    def __init__(self, filename: str, bytes_to_write: bytes, overwrite: bool = False, append: bool = False):
        self.path = Path(filename)
        self.append = append
        self.overwrite = overwrite
        self.bytes_to_write = bytes_to_write

    def instruction(self) -> int:
        if self.append:
            appendable_path = self.path.open('a')
            return appendable_path.write(self.bytes_to_write)

        return self.path.write_bytes(self.bytes_to_write)

    def validate(self) -> WriteBytes[Name, int]:
        if self.overwrite and self.append:
            raise ValueError('Cannot overwrite and append simultaneously')
        if self.path.exists() and not self.overwrite:
            raise FileExistsError(f'Cannot {str(self)} to {str(self.path)}')
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
