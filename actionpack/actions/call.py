from actionpack import Action
from actionpack.utils import Closure


class Call(Action):

    def __init__(self, closure: Closure):
        self.closure = closure

    def instruction(self):
        return self.closure()

