import logging
import time

from wshubsapi.Hub import Hub

from libs.MainApp import forceQuit

log = logging.getLogger(__name__)


class CodeHubException(Exception):
    pass


class WindowHub(Hub):
    def forceClose(self, _sender):
        log.info("Client: {} force us to close".format(_sender))
        time.sleep(1)
        forceQuit()
