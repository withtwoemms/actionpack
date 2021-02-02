from actionpack import Action
from pathlib import Path


class WriteBytes(Action):
    def __init__(self, filename: str, bytes_to_write: bytes):
        self.path = Path(filename)
        self.instruction = lambda: self.path.write_bytes(bytes_to_write)

    def validate(self):
        if self.path.exists():
            raise FileExistsError(f'Cannot {str(self)} to {str(self.path)}')
        if self.path.is_dir():
            raise IsADirectoryError(str(self.path))
        return self

