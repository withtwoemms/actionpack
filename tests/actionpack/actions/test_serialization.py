import json
import pickle

from datetime import datetime
from marshmallow import Schema
from marshmallow import fields
from unittest import TestCase

from actionpack.action import Result
from actionpack.actions.serialization import Serialization
from actionpack.utils import pickleable


class SerializationTest(TestCase):

    class UserSchema(Schema):
        name = fields.Str()
        email = fields.Email()
        created_at = fields.DateTime()

    class User:
        def __init__(self, name, email):
            self.name = name
            self.email = email
            self.created_at = datetime.now()

        def __repr__(self):
            return f'<User(name=\'{self.name}\')>'

    user_dict = {'name': 'Spencer Semien', 'email': 'spencer@semien.co'}

    def setUp(self):
        self.user = self.User(name="Skategoat", email="skate@goat.biz")

    def test_can_serialize_marshmallow(self):
        serialization = Serialization(self.UserSchema(), self.user)
        result = serialization.perform()

        self.assertIsInstance(result, Result)
        self.assertIsInstance(result.value, str)
        self.assertTrue(json.loads(result.value))

    def test_can_deserialize_marshmallow(self):
        deserialization = Serialization(self.UserSchema(), json.dumps(self.user_dict), inverse=True)
        result = deserialization.perform()

        self.assertIsInstance(result, Result)
        self.assertIsInstance(self.User(**result.value), self.User)

    def test_can_serialize_pickle(self):
        spickle = Serialization(pickle, self.user)
        serialized = spickle.perform()

        self.assertIsInstance(serialized, Result)
        self.assertIsInstance(serialized.value, bytes)

    def test_can_deserialize_pickle(self):
        respickle = Serialization(pickle, pickleable(self.user), inverse=True)
        deserialized = respickle.perform()

        self.assertIsInstance(deserialized, Result)
        self.assertIsInstance(deserialized.value, self.User)

    def test_can_pickle(self):
        action = Serialization(self.UserSchema(), self.user)
        pickled = pickleable(action)
        unpickled = pickle.loads(pickled)

        self.assertTrue(pickleable(action))
        self.assertEqual(str(unpickled.__dict__), str(action.__dict__))
