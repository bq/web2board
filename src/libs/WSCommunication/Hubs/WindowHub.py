import logging
import time

from wshubsapi.hub import Hub
from libs.MainApp import force_quit

log = logging.getLogger(__name__)


class WindowHub(Hub):
    def forceClose(self, _sender):
        log.info("Client: {} force us to close".format(_sender))
        time.sleep(1)
        force_quit()
