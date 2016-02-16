import json
import logging
import os
import time
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler

from libs import utils
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WSConnectionHandler(ConnectionHandler):
    def opened(self, *args):
        from libs.MainApp import getMainApp
        super(WSConnectionHandler, self).opened(*args)
        getMainApp().w2bGui.changeConnectedStatus()

    def closed(self, code, reason=None):
        super(WSConnectionHandler, self).closed(code, reason)
        if self._connectedClient.ID == "Bitbloq":
            log.info("Bitbloq disconnected, closing web2board...")
            time.sleep(1)
            if utils.areWeFrozen():
                os._exit(1)

    def received_message(self, message):
        if message.data == "version":  # bitbloq thinks we are in version 1
            # send an empty dict to alert bitbloq we are in version 2
            self._connectedClient.writeMessage(json.dumps(dict()))
        else:
            super(WSConnectionHandler, self).received_message(message)
