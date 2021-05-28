from actionpack import Action
from actionpack.action import Name


class ReadInput(Action[str, Name]):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def instruction(self) -> str:
        return input(self.prompt)
