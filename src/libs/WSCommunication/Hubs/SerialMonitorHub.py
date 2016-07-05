# coding=utf-8
import logging
import os
import serial
import time

from wshubsapi.connected_clients_group import ConnectedClientsGroup
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
                    log.warning("Error in serial port, check connection")
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
        time.sleep(2)  # we have to give time to really close the port

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
        self.subscribed_clients_ports = dict()

    def __on_received_callback(self, port, data):
        self.clients.get_subscribed_clients().received(port, data)
        self._get_subscribed_clients_to_port(port).received(port, data)

    def _get_subscribed_clients_to_port(self, port):
        if port not in self.subscribed_clients_ports:
            self.subscribed_clients_ports[port] = []
        clients = self.subscribed_clients_ports[port]

        self.subscribed_clients_ports[port] = list(filter(lambda c: not c.api_is_closed, clients))
        return ConnectedClientsGroup(clients, self.__class__.__HubName__)

    def start_connection(self, port, baudrate=9600):
        if self.is_port_connected(port):
            raise SerialMonitorHubException("Port {} already in use".format(port))

        self.serial_connections[port] = SerialConnection(port, baudrate, self.__on_received_callback)
        return True

    def close_connection(self, port):
        if port in self.serial_connections:
            self.serial_connections[port].close()
        self.clients.get_subscribed_clients().closed(port)
        self._get_subscribed_clients_to_port(port).closed(port)

    def write(self, port, data, _sender):
        if not self.is_port_connected(port):
            self.start_connection(port)

        self.serial_connections[port].write(data)
        self.clients.get_subscribed_clients().written(data, port, _sender.ID)

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

    def close_unused_connections(self):
        """
        Close all ports without any subscribed client (this only take into account subscribed_clients_port, not global)
        """
        for port in self.get_all_connected_ports():
            self._get_subscribed_clients_to_port(port)  # this function remove closed clients
            if len(self.subscribed_clients_ports[port]) == 0:
                self.close_connection(port)

    def subscribe_to_port(self, port, _sender):
        real_client = _sender.api_get_real_connected_client()
        if port not in self.subscribed_clients_ports:
            self.subscribed_clients_ports[port] = []

        if real_client in self.subscribed_clients_ports.get(port):
            return False
        self.subscribed_clients_ports[port].append(real_client)
        return True

    def unsubscribe_from_port(self, port, _sender):
        real_client = _sender.api_get_real_connected_client()
        if real_client in self.subscribed_clients_ports[port]:
            self.subscribed_clients_ports[port].remove(real_client)
            return True
        return False

    def get_subscribed_clients_ids_to_port(self, port):
        return [c.ID for c in self._get_subscribed_clients_to_port(port)]
