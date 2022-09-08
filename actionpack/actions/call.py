from actionpack import Action
from actionpack.action import Name
from actionpack.action import Outcome
from actionpack.utils import Closure


class Call(Action[Name, Outcome]):
    def __init__(self, closure: Closure[Outcome]):
        self.closure = closure

    def instruction(self) -> Outcome:
        return self.closure()

    def __repr__(self):
        return f'<Call({self.closure.func.__name__})>'
