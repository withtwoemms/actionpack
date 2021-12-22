from typing import TypeVar
from typing import Union

from actionpack import Action
from actionpack.action import Name


T = TypeVar('T')
Outcome = Union[str, T]


class Serialization(Action[Name, Outcome]):
    def __init__(self, schema=None, data=None, inverse=False):
        self.schema = schema
        self.data = data
        self.inverse = inverse

    def validate(self):
        if not self.data:
            raise self.NoDataGiven()
        if not self.schema:
            raise self.NoSchemaGiven()
        return self

    def instruction(self) -> Outcome:
        return self.schema.loads(self.data) if self.inverse else self.schema.dumps(self.data)

    class NoDataGiven(Exception):
        pass

    class NoSchemaGiven(Exception):
        pass
