from __future__ import annotations
from pathlib import Path

from actionpack import Action
from actionpack.action import Name


class Write(Action[Name, int]):
    def __init__(
        self,
        filename: str,
        to_write: str,
        prefix: str = None,
        overwrite: bool = False,
        append: bool = False,
    ):
        prefix_type, to_write_type = type(prefix), type(to_write)
        if prefix_type != to_write_type and to_write_type not in [bytes, str]:
            raise TypeError(f'Must be of type {to_write_type}: {prefix_type}')

        self.path = Path(filename)
        self.to_write = to_write
        self.prefix = prefix
        self.append = append
        self.overwrite = overwrite

    def instruction(self) -> str:
        if isinstance(self.to_write, bytes):
            mode, msg = 'ab', self.prefix if self.prefix else b'' + self.to_write
        elif isinstance(self.to_write, str):
            mode, msg = 'a', f"{self.prefix if self.prefix else ''}{self.to_write}"
        else:
            raise TypeError(f'Must be of str or bytes: {self.to_write}')

        if self.append:
            rchar = b'\n' if mode == 'ab' else '\n'
            self.path.open(mode).write(msg + rchar)
        else:
            self.path.write_bytes(msg) if isinstance(msg, bytes) else self.path.write_text(self.to_write)
        return str(self.path.absolute())

    def validate(self) -> Write[Name, int]:
        if self.overwrite and self.append:
            raise ValueError('Cannot overwrite and append simultaneously')
        if self.path.exists() and not self.overwrite and not self.append:
            raise FileExistsError(f'Cannot {str(self)} to {str(self.path)}')
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self
