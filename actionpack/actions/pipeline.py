from actionpack.utils import first
from actionpack.procedure import KeyedProcedure
from actionpack import Action
from actionpack.action import ActionType, Result

from inspect import BoundArguments
from inspect import signature
from oslash import Right
from typing import Dict


class Pipeline(Action):

    def __init__(self, action: Action, *action_types: ActionType):
        # self.first_result = action.perform()
        self.action = action
        self.action_types = action_types
        self._action_types = iter(self.action_types)

    def instruction(self):
        # return self.flush()
        return self.flush(self.action)

    # recursive
    def flush(self, given_action: Action = None):
        next_action_type = next(self)
        if next_action_type:
            print('>>>', next_action_type)
            # if next_action_type == FittingType:
            #     print('SUP!')
            if next_action_type.__name__ == 'Fitting':
                next_action_type_params = next_action_type.keywords
                print('PARAMS ->>', next_action_type_params)
            else:
                next_action_type_params = dict(signature(next_action_type.__init__).parameters.items())
                print('PARAMS ->', next_action_type_params)
            next_action_type_params.pop('self', None)
            next_action_type_params_keys = list(next_action_type_params.keys())
            first_key = next_action_type_params_keys[0] 
            # first_key = next_action_type_params_keys.pop(0)  # first is fine for now...
            if given_action.__class__.__name__ == 'Fitting':
                # kprs = {}
                kprs = given_action.keywords
            else:
                kprs = dict(KeyedProcedure(*(given_action.set(name=first_key),)).execute())
            print('PARAM_KEYS ->', next_action_type_params_keys)
            print('KPRS ->', kprs)
            # kprs.update({k: None for k in next_action_type_params_keys if k not in next_action_type_params})  # should allow control of None
            kprs.update({k: None for k in next_action_type_params_keys if k not in kprs})  # should allow control of None
            # kprs.update({k: None for k in next_action_type_params_keys if kprs.get(k, None) is None})  # should allow control of None
            print('KPRS *->', kprs)
            if given_action.__class__.__name__ == 'Fitting':
                keyed_result = kprs
            else:
                keyed_result = {k: r.value for k, r in kprs.items()}
            print('KEYED_RESULT ->', keyed_result)
            next_action = next_action_type(**keyed_result)
            # next_action = next_action_type(**kprs)
            print('<<<', next_action)
            return self.flush(next_action)

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
        self.signature = signature(action)
        self.args = args
        self.kwargs = kwargs

    def instruction(self):
        return self.signature.bind(*self.args, **self.kwargs)
