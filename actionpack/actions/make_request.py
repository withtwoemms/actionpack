from actionpack import Action

from requests import Request
from requests import Session
from validators import url as is_url



class MakeRequest(Action):

    methods = ('CONNECT', 'GET', 'DELETE', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE')

    def __init__(self, method: str, url: str, data: dict=None, headers: dict=None, session: Session=None):
        self.method = method.upper()
        self.url = url
        self.request = Request(method, self.url, data=data, headers=headers).prepare()
        self.session = session

    def instruction(self):
        return (self.session if self.session else Session()).send(self.request)

    def validate(self):
        if self.method not in self.methods:
            raise ValueError(f'Invalid HTTP method: {self.method}')
        url_validation = is_url(self.url)
        if url_validation is not True:
            raise url_validation
        return self

