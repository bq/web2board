import unittest

from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.Test.utils.HubsUtils import removeHubsSubclasses

from Test.testingUtils import createCompilerUploaderMock, createSenderMock
from libs.CompilerUploader import CompilerUploader

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock, flexmock_teardown

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub
from libs.MainApp import getMainApp


class TestSerialMonitorHub(unittest.TestCase):
    def setUp(self):
        global subprocess
        HubsInspector.inspectImplementedHubs(forceReconstruction=True)
        self.serialMonitorHub = flexmock(HubsInspector.getHubInstance(SerialMonitorHub))
        """:type : flexmock"""
        self.sender = createSenderMock()

        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()

    def tearDown(self):
        flexmock_teardown()
        removeHubsSubclasses()

    def test_changeBaudrate_doesNotClosePortIfNotCreated(self):
        port = "COM4"
        baudrate = 115200
        self.serialMonitorHub.should_receive("closeConnection").never()
        self.serialMonitorHub.should_receive("startConnection").with_args(port, baudrate).once()

        self.assertTrue(self.serialMonitorHub.changeBaudrate(port, baudrate))

    def test_changeBaudrate_closePortIfAlreadyCreated(self):
        port = "COM4"
        baudrate = 9600
        self.serialMonitorHub.serialConnections[port] = flexmock(isClosed=lambda: False, changeBaudRate=lambda *args: None)
        self.serialMonitorHub.serialConnections[port].should_receive("changeBaudRate").with_args(baudrate).once()

        self.assertTrue(self.serialMonitorHub.changeBaudrate(port, baudrate))

    def test_changeBaudrate_callsBaudrateChangedForSubscribed(self):
        port = "COM4"
        baudrate = 115200
        self.serialMonitorHub.should_receive("startConnection").with_args(port, baudrate).once()
        subscribedClients = flexmock(baudrateChanged=lambda p, b: None)
        clientsHolder = flexmock(self.serialMonitorHub._getClientsHolder(), getSubscribedClients=lambda :subscribedClients)
        clientsHolder.getSubscribedClients().should_receive("baudrateChanged").once()

        self.assertTrue(self.serialMonitorHub.changeBaudrate(port, baudrate))
