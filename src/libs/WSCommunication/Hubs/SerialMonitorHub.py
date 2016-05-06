# coding=utf-8
import logging
import os
import serial
import time
from wshubsapi.hub import Hub

from libs.CompilerUploader import CompilerUploader
from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager

log = logging.getLogger(__name__)


class SerialConnection:
    def __init__(self, port, baudrate, on_received_callback):
        self.serial = serial.Serial()
        self.serial.port = port
        self.serial.baudrate = baudrate
        self.serial.open()
        self.on_received_callback = on_received_callback
        self.__getData()
        self.is_about_to_be_closed = False

    @asynchronous()
    def __getData(self):
        while self.serial.isOpen():
            out = ''
            try:
                while self.serial.inWaiting() > 0:
                    out += self.serial.read(1)
                if out != '':
                    self.on_received_callback(self.serial.port, out)
            except IOError as e:
                if e.errno == 5 or e.message == "call to ClearCommError failed":
                    log.exception("Error in serial port, check connection")
                    self.close()
                else:
                    raise
            except Exception as e:
                if not self.is_about_to_be_closed:
                    log.exception("error getting data: {}".format(e))
            time.sleep(0.1)

    def write(self, data):
        self.serial.write(data.encode('utf-8', 'replace'))

    def change_baudrate(self, value):
        self.serial.close()
        self.serial.baudrate = value
        self.serial.open()

    def close(self):
        self.is_about_to_be_closed = True
        self.serial.close()
        time.sleep(2) #  we have to give time to really close the port

    def is_closed(self):
        return not self.serial.isOpen()


class SerialMonitorHubException(Exception):
    pass


class SerialMonitorHub(Hub):
    SERIAL_MONITOR_PATH = os.path.join(PathsManager.EXECUTABLE_PATH, "SerialMonitor")

    def __init__(self):
        super(SerialMonitorHub, self).__init__()
        self.serial_connections = dict()
        """:type : dict from int to SerialConnection"""

    def start_connection(self, port, baudrate=9600):
        if self.is_port_connected(port):
            raise SerialMonitorHubException("Port {} already in use".format(port))

        self.serial_connections[port] = SerialConnection(port, baudrate, self.__on_received_callback)
        return True

    def close_connection(self, port):
        if port in self.serial_connections:
            self.serial_connections[port].close()

    def write(self, port, data, _sender):
        if not self.is_port_connected(port):
            self.start_connection(port)

        self.serial_connections[port].write(data)
        self._getClientsHolder().getSubscribedClients().writted(data, port, _sender.ID)

    def change_baudrate(self, port, baudrate):
        if not self.is_port_connected(port):
            self.start_connection(port, baudrate)
        else:
            self.serial_connections[port].change_baudrate(baudrate)
        self.clients.get_subscribed_clients().baudrate_changed(port, baudrate)

    def get_available_ports(self):
        return CompilerUploader.construct().get_available_ports()

    def find_board_port(self, board):
        return CompilerUploader.construct(board).get_port()

    def is_port_connected(self, port):
        return port in self.serial_connections and not self.serial_connections[port].is_closed()

    def get_all_connected_ports(self):
        return [port for port, connection in self.serial_connections.items() if not connection.is_closed()]

    def close_all_connections(self):
        for port in self.get_all_connected_ports():
            self.close_connection(port)

    def __on_received_callback(self, port, data):
        self.clients.getSubscribedClients().received(port, data)
