from actionpack import Action


class ReadInput(Action):
    def __init__(self, prompt: str):
        self.instruction = lambda: input(prompt)

