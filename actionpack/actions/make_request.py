from actionpack import Action

from requests import Request
from requests import Session
from validators import url as is_url



class MakeRequest(Action):

    methods = ('CONNECT', 'GET', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE')

    def __init__(self, method: str, url: str, data: dict=None, headers: dict=None, session: Session=None):
        self.method = method.upper()
        self.url = url
        self.method = method
        self.data = data
        self.headers = headers
        self.session = session

    def prepare(self, method: str, url: str, data: dict=None, headers=None) -> Request:
        return Request(method, self.url, data=data, headers=headers).prepare()

    def instruction(self):
        request = self.prepare(self.method, self.url, self.data, self.headers)
        return (self.session if self.session else Session()).send(request)

    def validate(self):
        if self.method not in self.methods:
            raise ValueError(f'Invalid HTTP method: {self.method}')
        url_validation = is_url(self.url)
        if url_validation is not True:
            raise url_validation
        return self

