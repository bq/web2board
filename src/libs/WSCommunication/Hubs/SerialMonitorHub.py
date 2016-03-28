import logging
import os
import serial
import time
from wshubsapi.Hub import Hub

from libs.CompilerUploader import CompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)


class SerialConnection:
    def __init__(self, port, baudrate, onReceivedCallback):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.open()
        self.onReceivedCallback = onReceivedCallback
        self.__getData()
        self.isAboutToBeClosed = False

    @asynchronous()
    def __getData(self):
        while self.serial.isOpen():
            out = ''
            try:
                while self.serial.inWaiting() > 0:
                    out += self.serial.read(1)
                if out != '':
                    self.onReceivedCallback(self.serial.port, out)
            except Exception as e:
                if not self.isAboutToBeClosed:
                    log.exception("error getting data: {}".format(e))
            time.sleep(0.1)

    def write(self, data):
        data = data.replace("+", "\+")
        self.serial.write(data.encode())

    def changeBaudRate(self, value):
        self.serial.close()
        self.serial.baudrate = value
        self.serial.open()

    def close(self):
        self.isAboutToBeClosed = True
        self.serial.close()
        time.sleep(3) #we have to give time to really close the port

    def isClosed(self):
        return not self.serial.isOpen()


class SerialMonitorHubException(Exception):
    pass


class SerialMonitorHub(Hub):
    SERIAL_MONITOR_PATH = os.path.join(PathsManager.EXECUTABLE_PATH, "SerialMonitor")

    def __init__(self):
        super(SerialMonitorHub, self).__init__()
        self.serialConnections = dict()
        """:type : dict from int to SerialConnection"""

    def startApp(self, port, board):
        compilerUploader = CompilerUploader.construct(board)
        from libs.MainApp import getMainApp
        mainApp = getMainApp()
        if mainApp.w2bGui.isSerialMonitorRunning():
            port = mainApp.w2bGui.serialMonitor.port
        if port is None:
            port = compilerUploader.getPort()
        port = mainApp.w2bGui.startSerialMonitorApp(port).get()
        return port

    def startConnection(self, port, baudrate=9600):
        if self.isPortConnected(port):
            raise SerialMonitorHubException("Port {} already in use".format(port))

        self.serialConnections[port] = SerialConnection(port, baudrate, self.__onReceivedCallback)
        return True

    def closeConnection(self, port):
        self.serialConnections[port].close()

    def write(self, port, data, _sender):
        if not self.isPortConnected(port):
            self.startConnection(port)

        self.serialConnections[port].write(data)
        self._getClientsHolder().getSubscribedClients().writted(data, port, _sender.ID)

    def changeBaudrate(self, port, baudrate):
        if not self.isPortConnected(port):
            self.startConnection(port, baudrate)
        else:
            self.serialConnections[port].changeBaudRate(baudrate)
        self._getClientsHolder().getSubscribedClients().baudrateChanged(port, baudrate)
        return True

    def getAvailablePorts(self):
        return CompilerUploader.construct().getAvailablePorts()

    def findBoardPort(self, board):
        return CompilerUploader.construct(board).getPort()

    def isPortConnected(self, port):
        return port in self.serialConnections and not self.serialConnections[port].isClosed()

    def getAllConnectedPorts(self):
        return [port for port, connection in self.serialConnections.items() if not connection.isClosed()]

    def closeAllConnections(self):
        for port in self.getAllConnectedPorts():
            self.closeConnection(port)
        return True

    def __onReceivedCallback(self, port, data):
        self._getClientsHolder().getSubscribedClients().received(port, data)
