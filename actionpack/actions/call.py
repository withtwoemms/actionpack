from actionpack import Action
from actionpack.action import K
from actionpack.action import T
from actionpack.utils import Closure


class Call(Action[T, K]):
    def __init__(self, closure: Closure[T]):
        self.closure = closure

    def instruction(self) -> T:
        return self.closure()
