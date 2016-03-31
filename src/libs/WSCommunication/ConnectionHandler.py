import json
import logging
import os
import time
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler

import libs.MainApp
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
            time.sleep(0.5)
            if utils.areWeFrozen() or True:
                libs.MainApp.forceQuit()

    def received_message(self, message):
        if message.data == "version":  # bitbloq thinks we are in version 1
            # send an empty dict to alert bitbloq we are in version 2
            self._connectedClient.api_writeMessage(json.dumps(dict()))
        else:
            sortMessage = str(message) if len(message.data) < 500 else message.data[:300] + "..."
            log.debug("Message received from ID: %s\n%s " % (str(self._connectedClient.ID), sortMessage))
            self.commEnvironment.onAsyncMessage(self._connectedClient, message.data)
