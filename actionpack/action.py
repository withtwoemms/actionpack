from oslash import Left
from oslash import Right
from typing import List
from typing import Union


class Action:
    def perform(self) -> Union[Left, Right]:
        if callable(self.instruction):
            try:
                return Right(self.validate().instruction())
            except Exception as e:
                return Left(e)
        else:
            return Left(TypeError(f'Must be callable: {self.instruction}'))

    def validate(self):
        return self

    def __repr__(self):
        return f'{self.__class__.__name__}'

