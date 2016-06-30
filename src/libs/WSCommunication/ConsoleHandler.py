import logging
import sys
import time

from wshubsapi.comm_environment import CommEnvironment
from wshubsapi.connected_client import ConnectedClient

from libs import utils
from libs.Decorators.Asynchronous import asynchronous
from libs.LoggingUtils import init_logging
from libs.WSCommunication.ConsoleMessageParser import ConsoleMessageParser


class ConsoleHandler:
    log = logging.getLogger(__name__)

    def __init__(self):
        self.comm_environment = CommEnvironment.get_instance()
        self._connected_client = ConnectedClient(self.comm_environment, self.write_message)
        self.open("bitbloq")
        self.parser = ConsoleMessageParser()

    def data_received(self, chunk):
        pass

    def listener_loop(self):
        while True:
            message = raw_input()
            messages = self.parser.add_data(message)
            for m in messages:
                self.on_message(m.decode('utf-8'))

    def write_message(self, message, binary=False):
        self.log.info("%s%s%s", self.parser.INIT, message, self.parser.END)

    def open(self, name=None):
        client_id = name
        id_ = self.comm_environment.on_opened(self._connected_client, client_id)
        self.log.debug("open new connection with ID: {} ".format(id_))

    def on_message(self, message):
        self.log.debug(u"Message received from ID: {}\n{} ".format(self._connected_client.ID, message))
        self.comm_environment.on_message(self._connected_client, message)

    def on_close(self):
        pass

if __name__ == '__main__':
    c = ConsoleHandler()
    c.log = init_logging(__name__)
    utils.set_log_level(logging.DEBUG)
    c.log.debug("------------")
    c.log.info("Test")
    c.listener_loop()
