from actionpack import Action
from actionpack.action import Name


class Serialization(Action[Name, str]):
    def __init__(self, schema=None, data=None, inverse=False):
        self.schema = schema
        self.data = data
        self.validate()
        self.inverse = inverse

    def validate(self):
        if not self.data:
            raise self.NoDataGiven()
        if not self.schema:
            raise self.NoSchemaGiven()
        return self

    def instruction(self) -> str:
        return self.schema.loads(self.data) if self.inverse else self.schema.dumps(self.data)

    class NoDataGiven(Exception):
        pass

    class NoSchemaGiven(Exception):
        pass

