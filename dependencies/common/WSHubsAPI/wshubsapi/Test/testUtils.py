# coding=utf-8
import unittest
import time
from wshubsapi.ConnectedClient import ConnectedClient
from wshubsapi.Hub import Hub
from wshubsapi.utils import *

try:
    from unittest.mock import MagicMock
except:
    from mock import MagicMock


class TestUtils(unittest.TestCase):
    def test_ASCII_UpperCaseIsInitialized(self):
        randomExistingLetters = ["A", "Q", "P"]
        for letter in randomExistingLetters:
            self.assertIn(letter, ASCII_UpperCase, "letter in ASCII_UpperCase")

    def test_ASCII_UpperCaseDoesNotContainNotASCIICharacters(self):
        nonASCII_letter = "Ñ"
        self.assertNotIn(nonASCII_letter, ASCII_UpperCase)

    def test_getArgsReturnsAllArgumentsInMethod(self):
        class AuxClass:
            def auxFunc(self, x, y, z):
                pass

            @staticmethod
            def auxStatic(self, x, y):
                pass

            @classmethod
            def auxClassMethod(cls, x, y):
                pass
        testCases = [
            {"method": lambda x, y, z: x, "expected": ["x", "y", "z"]},
            {"method": lambda y=2, z=1: y, "expected": ["y", "z"]},
            {"method": lambda: 1, "expected": []},
            {"method": AuxClass().auxFunc, "expected": ["x", "y", "z"]},
            {"method": AuxClass.auxStatic, "expected": ["self", "x", "y"]},
            {"method": AuxClass.auxClassMethod, "expected": ["x", "y"]}
        ]
        for case in testCases:
            returnedFromFunction = getArgs(case["method"])

            self.assertEqual(returnedFromFunction, case["expected"])

    def test_getDefaultsReturnsTheDefaultValues(self):
        testCases = [
            {"method": lambda x, y, z: x, "expected": []},
            {"method": lambda y=2, z="a": y, "expected": [2, '"a"']},
            {"method": lambda x, y=4, z="ñoño": 1, "expected": [4, '"ñoño"']},
        ]
        for case in testCases:
            returnedFromFunction = getDefaults(case["method"])

            self.assertEqual(returnedFromFunction, case["expected"])

    def test_isFunctionForWSClient_IncludesStandardFunction(self):
        def thisIsANewFunction(test):
            print(test)

        self.assertTrue(isFunctionForWSClient(thisIsANewFunction), "new function is detected")

    def test_isFunctionForWSClient_ExcludesProtectedAndPrivateFunctions(self):
        def _thisIsAProtectedFunction(test):
            print(test)

        def __thisIsAPrivateFunction(test):
            print(test)

        self.assertFalse(isFunctionForWSClient(_thisIsAProtectedFunction), "protected function is excluded")
        self.assertFalse(isFunctionForWSClient(__thisIsAPrivateFunction), "private function is excluded")

    def test_isFunctionForWSClient_ExcludesAlreadyExistingFunctions(self):
        self.assertFalse(isFunctionForWSClient(Hub.HUBs_DICT), "excludes existing functions")

    def test_getModulePath_ReturnsTestUtilsPyModulePath(self):
        self.assertEqual(getModulePath(), os.getcwd() + os.sep + "Test")

    def setUp_WSMessagesReceivedQueue(self, MAX_WORKERS):
        queue = WSMessagesReceivedQueue()
        queue.DEFAULT_MAX_WORKERS = MAX_WORKERS
        return queue

    def test_WSMessagesReceivedQueue_Creates__MAX_WORKERS__WORKERS(self):
        queue = self.setUp_WSMessagesReceivedQueue(3)
        queue.executor.submit = MagicMock()

        queue.startThreads()

        self.assertTrue(queue.executor.submit.called)
        self.assertEqual(queue.executor.submit.call_count, queue.DEFAULT_MAX_WORKERS)

    def setUp_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop(self, MAX_WORKERS, message):
        queue = self.setUp_WSMessagesReceivedQueue(MAX_WORKERS)
        connectedClient = ConnectedClient(None, None, None, None)
        connectedClient.onMessage = MagicMock()
        connectedClient.onError = MagicMock()
        queue.get = MagicMock(return_value=[message, connectedClient])
        return queue, connectedClient

    def test_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop_CallsClientOnMessage(self):
        queue, connectedClient = self.setUp_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop(1, "message")

        queue.startThreads()
        time.sleep(0.02)
        queue.keepAlive = False

        connectedClient.onMessage.assert_called_with("message")

    def test_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop_CallsOnErrorIfRaisesException(self):
        queue, connectedClient = self.setUp_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop(1, "message")
        exception = Exception("test")
        connectedClient.onMessage.side_effect = exception

        queue.startThreads()
        time.sleep(0.02)
        queue.keepAlive = False

        connectedClient.onError.assert_called_with(exception)

    def test_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop_PrintExceptionIfConnectedClientIsNoConnectedClient(
            self):
        queue, connectedClient = self.setUp_WSMessagesReceivedQueue_infiniteOnMessageHandlerLoop(1, "message")
        queue.get = MagicMock(return_value=["message", None])

        queue.startThreads()
        time.sleep(0.02)
        queue.keepAlive = False

        self.assertFalse(connectedClient.onError.called)
        self.assertFalse(connectedClient.onMessage.called)
