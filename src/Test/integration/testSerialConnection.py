import unittest

from serial.serialutil import SerialException

from SerialMonitorDialog import SerialConnection
from libs import utils


class TestSerialConnection(unittest.TestCase):

    @unittest.skip("test not working")
    def test_construct_isAbleToConnectToSerialPort(self):
        port = utils.listSerialPorts()[0][0]
        try:
            self.serialConnection = SerialConnection(port)
        except SerialException as e:
            self.fail("unable to connect to port: {0} due to: {1}".format(port, e))
