from actionpack import Action


class Serialization(Action):
    def __init__(self, schema, data, inverse=False):
        self.schema = schema
        self.data = data
        self.inverse = inverse

    def instruction(self) -> str:
        return self.schema.loads(self.data) if self.inverse else self.schema.dumps(self.data)

