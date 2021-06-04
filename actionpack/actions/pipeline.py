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
    # def flush(self, keyed_result: dict = None):
    def flush(self, given_action: Action = None):
        next_action_type = next(self)
        if next_action_type:
            # if keyed_result:
            #     return action_type(**keyed_result).perform().value
            next_action_type_params = dict(signature(next_action_type.__init__).parameters.items())
            next_action_type_params.pop('self', None)
            # useful_params = {k: v for k, v in action_type_params if k != 'self'}
            next_action_type_params_keys = list(next_action_type_params.keys())
            # first_key = first(next_action_type_params_keys)  # first is fine for now...
            first_key = next_action_type_params_keys.pop(0)  # first is fine for now...
            # kp = dict(KeyedProcedure(*(self.start.set(name=key),)).execute())
            # kp = dict(KeyedProcedure(*(given_action.set(name=key),)).execute(should_raise=True))
            kprs = dict(KeyedProcedure(*(given_action.set(name=first_key),)).execute())
            kprs.update({k: None for k in next_action_type_params_keys})  # should allow control of None
            print(kprs)
            keyed_result = {k: r.value for k, r in kprs.items()}
            print(f'KEYED_RESULT: {keyed_result}')
            next_action = next_action_type(**keyed_result)
            return self.flush(next_action)
        else:
            return 'HELLO'
        #     if given_action:
        #         # return action_type(**keyed_result).perform().value
        #         pass
        #     else:
        #         # # TODO (withtwoemms) -- set the NAME of the action
        #         # action_type_params = dict(signature(action_type.__init__).parameters.items())
        #         # action_type_params.pop('self', None)
        #         # # useful_params = {k: v for k, v in action_type_params if k != 'self'}
        #         # key = first(list(action_type_params.keys()))
        #         # kp = dict(KeyedProcedure(*(self.start.set(name=key),)).execute())
        #         # keyed_result = {k: r.value for k, r in kp.items()}
        #         # action = action_type(**keyed_result)
        #         # # action_result = dict(KeyedProcedure(action).execute())
        #         # # return self.flush(keyed_result=keyed_result)
        #         return self.flush(next_action)
        # else:
        #     # TODO (withtwoemms) -- reconsider this behavior. may want to return None
        #     return keyed_result
        # # atype = next(self)
        # # if atype:
        # #     if result:
        # #         print('RESULT:', result)
        # #         return self.flush(atype(**result).perform().value)
        # #     else:
        # #         return self.flush(atype(self.first_result.value).perform().value)
        # #     #if result:
        # #     #    if isinstance(result, BoundArguments):
        # #     #        return self.flush(atype(*result, **result))
        # #     #    else:
        # #     #        return self.flush(atype(result).perform().value)
        # #     #else:
        # #     #    if isinstance(result, BoundArguments):
        # #     #        return self.flush(atype(*result, **result))
        # #     #    else:
        # #     #        return self.flush(atype(self.first_result.value).perform().value)
        # # else:
        # #     return result

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
        # return dict(zip(instance.keywords, instance.args))
        instance.keyed_values

    def __new__(mcs, keyed_results: Dict[str, Result]):
        dct = {
            '__init__': FittingType.init,
            'instruction': FittingType.instruction,
            'keyed_values': {k: r.value for k, r in keyed_results.items()}
        }
        cls = type('Fitting', (Action,), dct)

        return cls

    # def __new__(mcs, dct: dict = None, keywords: set = None):
    #     dct = dct if isinstance(dct, dict) else dict()
    #     dct['__init__'] = FittingType.init
    #     dct['instruction'] = FittingType.instruction
    #     keywords = keywords if isinstance(keywords, set) else set()
    #     dct['keywords'] = keywords
    #     cls = type('Fitting', (Action,), dct)
    #     return cls


class Fitting(Action):

    def __init__(self, action: Action, *args, **kwargs):
        self.signature = signature(action)
        self.args = args
        self.kwargs = kwargs

    def instruction(self):
        return self.signature.bind(*self.args, **self.kwargs)
