# coding=utf-8
try:
    import thread
except ImportError:
    import _thread as thread
import unittest

from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.CommEnvironment import CommEnvironment
from wshubsapi.ConnectedClientsHolder import ConnectedClientsHolder
from wshubsapi.utils import WSMessagesReceivedQueue

try:
    from unittest.mock import MagicMock
except:
    from mock import MagicMock


class TestCommProtocol(unittest.TestCase):
    def setUp(self):
        self.commEnvironment = CommEnvironment(maxWorkers=0, unprovidedIdTemplate="unprovided_{}")

    def test_construct_initializeMandatoryAttributes(self):
        self.assertIsInstance(self.commEnvironment.wsMessageReceivedQueue, WSMessagesReceivedQueue)
        self.assertIsInstance(self.commEnvironment.lock, thread.LockType)
        self.assertIs(self.commEnvironment.allConnectedClients, ConnectedClientsHolder.allConnectedClients)

    def test_ConstructConnectedClient_returnsConnectedClient(self):
        def w():
            pass

        def c():
            pass

        serialization = "serialization"
        connectedClient = self.commEnvironment.constructConnectedClient(w, c, serialization)

        self.assertEqual(connectedClient.writeMessage, w)
        self.assertEqual(connectedClient.close, c)
        self.assertEqual(connectedClient.pickler, serialization)

    def test_getUnprovidedID_returnsFirstAvailableUnprovidedID(self):
        firstClient = ConnectedClient(None, self.commEnvironment, lambda x: x, lambda z: z)
        secondClient = ConnectedClient(None, self.commEnvironment, lambda x: x, lambda z: z)
        firstClient.onOpen()  # first UnprovidedID = unprovided_0
        secondClient.onOpen()  # first UnprovidedID = unprovided_1

        unprovidedId = self.commEnvironment.getUnprovidedID()

        self.assertEqual(unprovidedId, "unprovided_2")

    def test_getUnprovidedID_returnAvailableUnprovidedIdsIfExist(self):
        self.commEnvironment.availableUnprovidedIds.append("availableId_1")

        unprovidedId = self.commEnvironment.getUnprovidedID()

        self.assertEqual(unprovidedId, "availableId_1")

    def test_getUnprovidedID_availableIdsAreRemovedWhenUsed(self):
        self.commEnvironment.availableUnprovidedIds.append("availableId_1")
        unprovidedId1 = self.commEnvironment.getUnprovidedID()
        unprovidedId2 = self.commEnvironment.getUnprovidedID()

        self.assertEqual(unprovidedId2, "unprovided_0")