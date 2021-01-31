from actionpack import Action


class FakeAction(Action):

    result = f'Performing Action.'

    def __init__(self, exception=None):
        self.exception = exception
        self.instruction = lambda: self.result

    def validate(self):
        if self.exception:
            raise self.exception
        return super().validate()

