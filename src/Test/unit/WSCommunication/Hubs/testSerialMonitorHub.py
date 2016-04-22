import unittest

from wshubsapi.hubs_inspector import HubsInspector
from wshubsapi.test.utils.hubs_utils import remove_hubs_subclasses

from Test.testingUtils import createCompilerUploaderMock, createSenderMock

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock, flexmock_teardown

from libs.WSCommunication.Hubs.SerialMonitorHub import SerialMonitorHub


class TestSerialMonitorHub(unittest.TestCase):
    def setUp(self):
        global subprocess
        HubsInspector.inspect_implemented_hubs(force_reconstruction=True)
        self.serialMonitorHub = flexmock(HubsInspector.get_hub_instance(SerialMonitorHub))
        """:type : flexmock"""
        self.sender = createSenderMock()

        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()

    def tearDown(self):
        flexmock_teardown()
        remove_hubs_subclasses()

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
        clientsHolder = flexmock(self.serialMonitorHub.clients, get_subscribed_clients=lambda: subscribedClients)
        clientsHolder.get_subscribed_clients().should_receive("baudrateChanged").once()

        self.assertTrue(self.serialMonitorHub.changeBaudrate(port, baudrate))
