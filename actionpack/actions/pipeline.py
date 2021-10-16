from collections import OrderedDict
from inspect import BoundArguments
from inspect import signature
from oslash import Right
from typing import Dict
from typing import Optional

from actionpack.utils import first
from actionpack.procedure import KeyedProcedure
from actionpack import Action
from actionpack.action import ActionType, Result


class Pipeline(Action):

    def __init__(self, action: Action, *action_types: ActionType):
        # self.first_result = action.perform()
        self.action = action
        self.action_types = action_types
        self._action_types = iter(self.action_types)

    def instruction(self):
        return self.flush(self.action).perform(should_raise=True).value

    # recursive
    def flush(self, given_action: Optional[Action] = None) -> Action:
        next_action_type = next(self)

        if next_action_type:
            params_dict = OrderedDict(signature(next_action_type.__init__).parameters.items())
            params_dict.pop('self', None)
            params = list(params_dict.keys())
            keyed_result = dict(zip(params, [given_action.perform(should_raise=True).value]))
            if isinstance(next_action_type, Fitting):
                params_dict = OrderedDict(signature(next_action_type.action.__init__).parameters.items())
                params_dict.pop('self', None)
                params = list(params_dict.keys())
                keyed_result = dict(zip(params, [keyed_result['action']]))
                next_action_type.kwargs.update(keyed_result)
                next_action = next_action_type.action(*next_action_type.args, **next_action_type.kwargs)
            else:
                next_action = next_action_type(**keyed_result)
                
            return self.flush(next_action)
        
        return given_action

    def __iter__(self):
        return self._action_types

    def __next__(self):
        try:
            return next(self._action_types)
        except StopIteration:
            self._action_types = iter(self._action_types)


class FittingType(type):

    @staticmethod
    def init(instance, **kwargs):
        print('INSTANCE', instance)
        print('KWARGS', kwargs)
        setattr(instance, 'keywords', kwargs)
        # setattr(instance, 'kwargs', kwargs)

    # @staticmethod
    # def init(instance, *args):
    #     print('INSTANCE', instance)
    #     print('ARGS', args)
    #     setattr(instance, 'args', args)
    #     #for i, arg in enumerate(args):
    #     #    setattr(instance, f'arg{i}', arg)

    @staticmethod
    def instruction(instance):
        # return dict(zip(instance.keywords, instance.args))
        instance.keyed_values

    # def __new__(mcs, keyed_results: Dict[str, Result]):
    #     dct = {
    #         '__init__': FittingType.init,
    #         'instruction': FittingType.instruction,
    #         'keyed_values': {k: r.value for k, r in keyed_results.items()}
    #     }
    #     cls = type('Fitting', (Action,), dct)

    #     return cls

    # def __new__(mcs, dct: dict = None, keywords: set = None):
    def __new__(mcs, dct: dict = None, keywords: dict = None):
        dct = dct if isinstance(dct, dict) else dict()
        dct['__init__'] = FittingType.init
        dct['instruction'] = FittingType.instruction
        # keywords = keywords if isinstance(keywords, set) else set()
        keywords = keywords if isinstance(keywords, dict) else dict()
        dct['keywords'] = keywords
        cls = type('Fitting', (Action,), dct)
        return cls


class Fitting(Action):

    def __init__(self, action: Action, *args, **kwargs):
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.signature = signature(action.__init__)

    def instruction(self):
        return self.action.perform()
