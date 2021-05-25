from actionpack import Action
from actionpack.action import K


class ReadInput(Action[str, K]):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def instruction(self) -> str:
        return input(self.prompt)
