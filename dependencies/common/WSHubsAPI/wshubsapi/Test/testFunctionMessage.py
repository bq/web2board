# coding=utf-8
import json
import unittest

from wshubsapi.ConnectedClientsGroup import ConnectedClientsGroup
from wshubsapi.FunctionMessage import FunctionMessage
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Hub import Hub
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses


class TestFunctionMessage(unittest.TestCase):
    def setUp(self):
        class TestHub(Hub):
            def testMethod(self, x, _sender, y=1):
                return x, _sender, y

            def testException(self):
                raise Exception("MyException")

            def testNoSender(self, x):
                return x

            def testReplayUnsuccessful(self, x):
                return self._constructUnsuccessfulReplay(x)

        self.testHubClass = TestHub
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.testHubInstance = HubsInspector.getHubInstance(self.testHubClass)

    def tearDown(self):
        del self.testHubClass
        del self.testHubInstance
        removeHubsSubclasses()

    def __constructMessageStr(self, hub="TestHub", function="testMethod", ID=1, args=list()):
        message = {
            "hub": hub,
            "function": function,
            "args": args,
            "ID": ID
        }
        return json.dumps(message)

    def test_FunctionMessageConstruction_InitializeNecessaryAttributes(self):
        fn = FunctionMessage(self.__constructMessageStr(), "connectedClient")

        self.assertEqual(fn.hubInstance, self.testHubInstance)
        self.assertEqual(fn.hubName, self.testHubClass.__HubName__)
        self.assertEqual(fn.args, [])
        self.assertEqual(fn.method, self.testHubInstance.testMethod)
        self.assertEqual(fn.connectedClient, "connectedClient")

    def test_FunctionMessageConstruction_WithUnrealMethodNameRaisesAnError(self):
        message = self.__constructMessageStr(function="notExists")
        self.assertRaises(AttributeError, FunctionMessage, message, "connectedClient")

    def test_CallFunction_ReturnsAnExpectedReplayMessageIfSuccess(self):
        fn = FunctionMessage(self.__constructMessageStr(args=["x"], ID=15, function="testNoSender"), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["replay"], "x")
        self.assertEqual(functionResult["success"], True)
        self.assertEqual(functionResult["hub"], self.testHubClass.__HubName__)
        self.assertEqual(functionResult["function"], "testNoSender")
        self.assertEqual(functionResult["ID"], 15)

    def test_CallFunction_ReturnsAnExpectedReplayMessageIfNoSuccess(self):
        fn = FunctionMessage(self.__constructMessageStr(ID=15, function="testException"), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["success"], False)
        self.assertEqual(functionResult["hub"], self.testHubClass.__HubName__)
        self.assertEqual(functionResult["function"], "testException")
        self.assertEqual(functionResult["ID"], 15)

    def test_CallFunction_IncludesSender(self):
        fn = FunctionMessage(self.__constructMessageStr(args=["x"]), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["replay"][0], "x")
        self.assertIsInstance(functionResult["replay"][1], ConnectedClientsGroup)
        self.assertEqual(functionResult["replay"][1][0], "_sender")
        self.assertEqual(functionResult["replay"][2], 1)
        self.assertEqual(functionResult["success"], True)

    def test_CallFunction_DoesNotIncludesSenderIfNotRequested(self):
        fn = FunctionMessage(self.__constructMessageStr(args=["x"], function="testNoSender"), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["replay"], "x")
        self.assertEqual(functionResult["success"], True)

    def test_CallFunction_SuccessFalseIfMethodRaisesException(self):
        fn = FunctionMessage(self.__constructMessageStr(function="testException"), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["success"], False)
        self.assertEqual(functionResult["replay"], "MyException")

    def test_CallFunction_ReplaysSuccessFalseIfReturnsUnsuccessfulReplayObject(self):
        fn = FunctionMessage(self.__constructMessageStr(function="testReplayUnsuccessful", args=["x"]), "_sender")

        functionResult = fn.callFunction()

        self.assertEqual(functionResult["success"], False)
        self.assertEqual(functionResult["replay"], "x")
