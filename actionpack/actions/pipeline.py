from actionpack import Action
from actionpack.action import ActionType

from inspect import BoundArguments
from inspect import signature
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
                print('RESULT:', result)
                return self.flush(atype(**result).perform().value)
            else:
                return self.flush(atype(self.first_result.value).perform().value)
            #if result:
            #    if isinstance(result, BoundArguments):
            #        return self.flush(atype(*result, **result))
            #    else:
            #        return self.flush(atype(result).perform().value)
            #else:
            #    if isinstance(result, BoundArguments):
            #        return self.flush(atype(*result, **result))
            #    else:
            #        return self.flush(atype(self.first_result.value).perform().value)
        else:
            return result

    def __iter__(self):
        return self._action_types

    def __next__(self):
        try:
            return next(self._action_types)
        except StopIteration:
            self._action_types = iter(self._action_types)


class FittingType(type):

    @staticmethod
    def init(instance, *args):
        setattr(instance, 'args', args)
        #for i, arg in enumerate(args):
        #    setattr(instance, f'arg{i}', arg)

    @staticmethod
    def instruction(instance):
        return dict(zip(instance.keywords, instance.args))

    def __new__(mcs, dct: dict = None, keywords: set = None):
        dct = dct if isinstance(dct, dict) else dict()
        dct['__init__'] = FittingType.init
        dct['instruction'] = FittingType.instruction
        keywords = keywords if isinstance(keywords, set) else set()
        dct['keywords'] = keywords
        cls = type('Fitting', (Action,), dct)
        return cls


class Fitting(Action):

    def __init__(self, action: Action, *args, **kwargs):
        self.signature = signature(action)
        self.args = args
        self.kwargs = kwargs

    def instruction(self):
        return self.signature.bind(*self.args, **self.kwargs)

