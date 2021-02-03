from requests import Response


class FakeResponse(Response):
    def __init__(self, content: bytes=bytes(), status: int=200):
        self._content = content
        self.status_code = status

