import json
import logging
import os
import time
from wshubsapi.ConnectionHandlers.Tornado import ConnectionHandler

import libs.MainApp
from libs import utils
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WSConnectionHandler(ConnectionHandler):
    def open(self, *args):
        from libs.MainApp import getMainApp
        super(WSConnectionHandler, self).open(*args)
        getMainApp().w2bGui.changeConnectedStatus()

    def on_close(self):
        super(WSConnectionHandler, self).on_close()
        if self._connectedClient.ID == "Bitbloq":
            log.info("Bitbloq disconnected, closing web2board...")
            time.sleep(0.5)
            if utils.areWeFrozen() or True:
                libs.MainApp.forceQuit()

    def on_message(self, message):
        if message == "version":  # bitbloq thinks we are in version 1
            # send an empty dict to alert bitbloq we are in version 2
            self._connectedClient.api_writeMessage(json.dumps(dict()))
        else:
            sortMessage = str(message) if len(message) < 500 else message[:300] + "..."
            log.debug("Message received from ID: %s\n%s " % (str(self._connectedClient.ID), sortMessage))
            self.commEnvironment.onAsyncMessage(self._connectedClient, message)
