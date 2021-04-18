from actionpack import Action
from actionpack.action import ActionType
from actionpack.action import ActionType

from oslash import Right


class Pipeline(Action):

    def __init__(self, action: Action, *action_types: ActionType):
        self.first_result = action.perform()
        self.action_types = action_types
        self._action_types = iter(self.action_types)

    def instruction(self):
        return self.flush()

    def flush(self, result=None):
        atype = next(self)
        if atype:
            if result:
                return self.flush(atype(result).perform().value)
            else:
                return self.flush(atype(self.first_result.value).perform().value)
        else:
            return result

    def __iter__(self):
        return self._action_types

    def __next__(self):
        try:
            return next(self._action_types)
        except StopIteration:
            self._action_types = iter(self._action_types)

