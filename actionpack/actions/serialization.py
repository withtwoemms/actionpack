from actionpack import Action
from actionpack.action import Name


class Serialization(Action[Name, str]):
    def __init__(self, schema, data, inverse=False):
        self.schema = schema
        self.data = data
        self.inverse = inverse

    def instruction(self) -> str:
        return self.schema.loads(self.data) if self.inverse else self.schema.dumps(self.data)
