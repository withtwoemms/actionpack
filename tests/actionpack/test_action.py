import pickle

from functools import reduce
from oslash import Left
from oslash import Right
from threading import Thread
from unittest import TestCase
from unittest.mock import patch

from actionpack import Action
from actionpack import partialaction
from actionpack.action import Result
from actionpack.utils import pickleable
from tests.actionpack import FakeAction
from tests.actionpack import FakeFile
from tests.actionpack.actions import FakeWrite


class ActionTest(TestCase):

    def raise_failure(self):
        raise self.exception

    def setUp(self) -> None:
        self.exception = Exception('something went wrong :/')

    def test_Action_returning_exception_does_not_have_successful_Result(self):
        result = FakeAction(instruction_provider=lambda: self.exception).perform()
        self.assertIsInstance(result, Result)
        self.assertFalse(result.successful)

    def test_Action_initialized_with_Exception_has_unsuccessful_Result(self):
        result = FakeAction(self.exception).perform()
        self.assertIsInstance(result, Result)
        self.assertFalse(result.successful)

    def test_Action_produces_Result_result_when_performed(self):
        result = FakeAction().perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, FakeAction.result)

    def test_Action_produces_Result_if_exception_raised_when_performed(self):
        result = FakeAction(instruction_provider=self.raise_failure).perform()
        self.assertIsInstance(result, Result)
        self.assertEqual(result.value, self.exception)

    def test_Action_can_raise_exception(self):
        with self.assertRaises(type(self.exception)):
            FakeAction(instruction_provider=self.raise_failure).perform(should_raise=True)

    def test_can_create_partial_Action(self):
        def instruction_provider():
            return some_result_value

        some_result_value = 'success!'
        PartialAction = partialaction(
            'FakeActionWithInstruction',
            FakeAction,
            instruction_provider=instruction_provider
        )
        self.assertEqual(PartialAction().perform().value, some_result_value)

    def test_can_determine_if_Result_was_successful(self):
        success = FakeAction().perform()
        failure = FakeAction(instruction_provider=self.raise_failure).perform()

        self.assertTrue(success.successful)
        self.assertFalse(failure.successful)

    def test_can_react_to_failure(self):
        vessel = []
        contents = 'contents'

        def fill():
            vessel.append(contents)

        self.assertNotIn(contents, vessel)

        reaction = FakeAction(instruction_provider=fill)
        action = FakeAction(
            instruction_provider=self.raise_failure,
            reaction=reaction
        )
        result = action.perform()

        self.assertFalse(result.successful)
        self.assertIn(contents, vessel)

    @patch('oslash.Left.__init__')
    def test_can_react_to_failure_during_catastrophe(self, mock_wrapper):
        def raise_another_failure(e):
            raise e

        mock_wrapper.side_effect = raise_another_failure

        vessel = []
        contents = 'contents'

        def fill():
            vessel.append(contents)

        reaction = FakeAction(instruction_provider=fill)
        action = FakeAction(
            instruction_provider=self.raise_failure,
            reaction=reaction
        )

        with self.assertRaises(Exception):
            result = action.perform()
            self.assertFalse(result.successful)

        self.assertIn(contents, vessel)

    def test_Action_Construct(self):
        construct = FakeAction(typecheck='Action instantiation fails.')
        result = construct.perform()
        self.assertEqual(construct.failure, result.value)
        self.assertIsInstance(construct, Action.Construct)
        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, Exception)

    def test_Action_can_be_serialized(self):
        action = FakeAction()
        pickled = pickle.dumps(action)
        unpickled = pickle.loads(pickled)

        self.assertEqual(pickleable(action), pickled)
        self.assertEqual(unpickled.result, action.result)
        self.assertEqual(unpickled.state, action.state)

    def test_can_safely_perform_Actions_concurrently(self):
        file = FakeFile(b'Hello.', 'wb')

        def perform_and_collect(action: Action, results: list):
            action.perform()
            results.append(file.read())

        initial_file_contents = file.read()
        action1 = FakeWrite(file, b' How are you?', delay=0.2)
        action2 = FakeWrite(file, b' I hope you\'re well.', delay=0.1)
        results = [initial_file_contents]
        thread1 = Thread(target=perform_and_collect, args=(action1, results))
        thread2 = Thread(target=perform_and_collect, args=(action2, results))
        threads = thread1, thread2
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

        self.assertEqual(
            reduce(lambda a, b: a + b, results),
            initial_file_contents + action1.to_write + action2.to_write
        )

    def test_Action_can_be_renamed(self):
        action = FakeAction()
        self.assertIsNone(action.name)
        name1 = 'new'
        action.set(name=name1)
        self.assertEqual(action.name, name1)
        name2 = 'different name'
        action.name = name2
        self.assertEqual(action.name, name2)

    def test_Action_has_unimplemented_instruction(self):
        Action().instruction()

    def test_can_delete_Action_name(self):
        action = FakeAction()
        action_name = 'gone soon.'
        action.set(name=action_name)
        self.assertEqual(action.name, action_name)
        del action.name

    def test_Action_perform_fails_for_non_callable_instruction(self):
        action = FakeAction(instruction_provider='nope.')
        result = action.perform()
        self.assertFalse(result.successful)
        self.assertIsInstance(result.value, TypeError)

    def test_can_compare_Actions(self):
        fake_action = FakeAction()
        self.assertTrue(fake_action == FakeAction())
        with self.assertRaises(Action.NotComparable):
            fake_action == '<fake_action>'

    def test_Action_Construct_has_string_representation(self):
        failed_action_instantiation = FakeAction(typecheck=True)
        result = failed_action_instantiation.perform()
        self.assertIsInstance(failed_action_instantiation, Action.Construct)
        self.assertEqual(repr(failed_action_instantiation), f'<Action.Construct[{result.value.__class__.__name__}]>')

    def test_partial_Action_has_string_representation(self):
        partial_action_name = 'FakeActionWithInstruction'
        PartialAction = partialaction(
            partial_action_name,
            FakeAction,
            instruction_provider=lambda: 'success!'
        )
        self.assertEqual(repr(PartialAction()), f'<{partial_action_name}>')

    def test_DependencyCheck_fails_if_package_missing(self):
        FakeAction.requirements = ('not-a-real-packing-never-will-be',)
        with self.assertRaises(Action.DependencyCheck.PackageMissing):
            FakeAction().check_dependencies(FakeAction)

    def test_DependencyCheck_fails_if_requirement_absent(self):
        with self.assertRaises(Action.DependencyCheck.WhichPackage):
            Action.DependencyCheck(FakeAction)


class ResultTest(TestCase):

    def raise_failure(self):
        raise self.exception

    def test_Result_success_is_immutable(self):
        success = FakeAction().perform()
        failure = FakeAction(instruction_provider=self.raise_failure).perform()

        with self.assertRaises(AttributeError):
            success.successful = 'nah.'

        with self.assertRaises(AttributeError):
            failure.successful = 'maybe?'

    def test_Result_has_timestamp(self):
        result = FakeAction(instruction_provider=lambda: 'succeeded').perform(
            timestamp_provider=lambda: 0
        )

        self.assertTrue(result.successful)
        self.assertEqual(result.produced_at, 0)

    def test_cannot_instantiate_without_Either(self):
        with self.assertRaises(Result.OutcomeMustBeOfTypeEither):
            Result('not an Either type')

    def test_cannot_change_immutable_attributes(self):
        result = Result(Right('correct.'))
        with self.assertRaises(AttributeError):
            result.produced_at = 123
        with self.assertRaises(AttributeError):
            result.successful = False
        with self.assertRaises(AttributeError):
            result.value = 'some other value'

        result.who_cares = 'right?'  # should not raise since not declared immutable

    def test_cannot_delete_immutable_attributes(self):
        result = Result(Right('correct.'))
        with self.assertRaises(AttributeError):
            del result.produced_at
        with self.assertRaises(AttributeError):
            del result.successful
        with self.assertRaises(AttributeError):
            del result.value

        result.who_cares = 'right?'
        del result.who_cares  # should not raise since not declared immutable

    def test_can_serialize_result(self):
        successful_outcome = 'correct.'
        successful_result = Result(Right(successful_outcome))
        self.assertEqual(str(successful_result), f'<Result|success[{type(successful_outcome).__name__}]>')

        unsuccessful_outcome = RuntimeError('incorrect.')
        unsuccessful_result = Result(Right(unsuccessful_outcome))
        self.assertEqual(str(unsuccessful_result), f'<Result|success[{type(unsuccessful_outcome).__name__}]>')

        confused_result = Result(Left(successful_outcome))
        self.assertFalse(confused_result.successful)
