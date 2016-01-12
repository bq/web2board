import datetime
from jsonpickle.pickler import Pickler

from wshubsapi import utils
from wshubsapi.ConnectedClient import ConnectedClient
import json
import unittest


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.connectedClient = ConnectedClient(serializationPickler=Pickler(max_depth=5, max_iter=80, make_refs=False),
                                               commEnvironment=None,
                                               writeMessageFunction=lambda x: x,
                                               closeFunction=lambda y: y)
        utils.setSerializerDateTimeHandler()

    def test_basicObjectSerialization(self):
        serialization = utils.serializeMessage(self.connectedClient.pickler, 5)
        self.assertTrue(serialization == '5', 'number serialization')
        serialization = utils.serializeMessage(self.connectedClient.pickler, "hi")
        self.assertTrue(serialization == '"hi"', 'str serialization')

    def test_simpleObjects(self):
        class SimpleObject(object):
            def __init__(self):
                self.a = 1
                self.b = "hi"

        serialization = utils.serializeMessage(self.connectedClient.pickler, SimpleObject())
        self.assertTrue(json.loads(serialization)["a"] == 1)
        self.assertTrue(json.loads(serialization)["b"] == "hi")

    def test_complexObjects(self):
        class ComplexObject(object):
            def __init__(self):
                self.a = {"a": 10, 1: 15}
                self.b = [1, 2, "hola"]

        serialization = utils.serializeMessage(self.connectedClient.pickler, ComplexObject())
        serObject = json.loads(serialization)
        self.assertTrue(isinstance(serObject["a"], dict))
        self.assertTrue(serObject["a"]["a"] == 10)
        self.assertTrue(serObject["a"]["1"] == 15)
        self.assertTrue(len(serObject["b"]) == 3)

    def test_cycleRef(self):
        class ComplexObject(object):
            def __init__(self):
                self.a = self

        serialization = utils.serializeMessage(self.connectedClient.pickler, ComplexObject())
        serObject = json.loads(serialization)
        self.assertTrue("ComplexObject" in serObject["a"])

    def test_dateTimeObjects(self):
        date = datetime.datetime.now()
        serialization = utils.serializeMessage(self.connectedClient.pickler, {"datetime": date})
        self.assertTrue(json.loads(serialization)["datetime"] == date.strftime(utils.DATE_TIME_FORMAT),
                        'datetime serialization')

        date = datetime.date(2001, 1, 1)
        serialization = utils.serializeMessage(self.connectedClient.pickler, {"datetime": date})
        self.assertTrue(json.loads(serialization)["datetime"] == date.strftime(utils.DATE_TIME_FORMAT),
                        'datetime serialization')

        date = datetime.time()
        serialization = utils.serializeMessage(self.connectedClient.pickler, {"datetime": date})
        self.assertTrue(json.loads(serialization)["datetime"] == date.strftime(utils.DATE_TIME_FORMAT),
                        'datetime serialization')


if __name__ == '__main__':
    unittest.main()
