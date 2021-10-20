from collections import OrderedDict
from inspect import signature
from typing import Optional

from actionpack import Action
from actionpack.action import ActionType
from actionpack.actions import Call
from actionpack.utils import first
from actionpack.utils import key_for
from actionpack.utils import swap


class Pipeline(Action):

    def __init__(self, action: Action, *action_types: ActionType, should_raise: bool = False):
        self.action = action
        self.should_raise = should_raise

        for action_type in action_types:
            if not isinstance(action_type, ActionType):
                raise TypeError(f'Must be an {ActionType.__name__}: {action_type}')

        self.action_types = action_types
        self._action_types = iter(self.action_types)

    def instruction(self):
        return self.flush(self.action).perform(should_raise=self.should_raise).value

    # recursive
    def flush(self, given_action: Optional[Action] = None) -> Action:
        next_action_type = next(self)

        if next_action_type:
            params_dict = OrderedDict(signature(next_action_type.__init__).parameters.items())
            params_dict.pop('self', None)
            params = list(params_dict.keys())
            keyed_result = dict(zip(params, [given_action.perform(should_raise=self.should_raise).value]))
            if next_action_type.__name__ == Pipeline.Fitting.__name__:
                params_dict = OrderedDict(signature(next_action_type.action.__init__).parameters.items())
                params_dict.pop('self', None)
                params = list(params_dict.keys())
                conduit = first(params)
                if conduit in next_action_type.kwargs and key_for(Pipeline.Receiver, next_action_type.kwargs):
                    params = swap(
                        params, 0,
                        params.index(key_for(Pipeline.Receiver, next_action_type.kwargs))
                    )
                keyed_result = dict(zip(params, [keyed_result['action']]))
                next_action_type.kwargs.update(keyed_result)
                next_action = next_action_type.action(**next_action_type.kwargs)
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

    class Receiver:
        pass

    class Fitting(type):

        @staticmethod
        def init(
            action: Action,
            should_raise: bool = False,
            reaction: Call = None,
            *args, **kwargs
        ):
            pass

        @staticmethod
        def instruction(instance):
            action_performance = instance.action.perform(should_raise=instance.should_raise)
            if action_performance.successful and instance.reaction:
                return instance.reaction.perform(should_raise=instance.should_raise)
            return action_performance

        def __new__(
            mcs,
            action: Action,
            should_raise: bool = False,
            reaction: Call = None,
            **kwargs
        ):
            dct = dict()
            dct['__init__'] = Pipeline.Fitting.init
            dct['instruction'] = Pipeline.Fitting.instruction
            dct['action'] = action
            dct['should_raise'] = should_raise
            dct['reaction'] = reaction
            dct['kwargs'] = kwargs
            cls = type(Pipeline.Fitting.__name__, (Action,), dct)
            return cls
