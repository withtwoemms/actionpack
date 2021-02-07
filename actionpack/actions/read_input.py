from actionpack import Action


class ReadInput(Action):
    def __init__(self, prompt: str):
        self.prompt = prompt

    def instruction(self) -> str:
        return input(self.prompt)

