import json
import logging

from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WSConnectionHandler(ConnectionHandler):
    def opened(self, *args):
        from libs.MainApp import getMainApp
        self._connectedClient = self.commEnvironment.constructConnectedClient(self.writeMessage)
        clientId = "Bitbloq"
        self.ID = self._connectedClient.onOpen(clientId)
        log.debug("open new connection with ID: %s " % str(self.ID))
        getMainApp().w2bGui.changeConnectedStatus()

    def closed(self, code, reason=None):
        super(WSConnectionHandler, self).closed(code, reason)

    def received_message(self, message):
        if message.data == "version":  # bitbloq thinks we are in version 1
            # send an empty dict to alert bitbloq we are in version 2
            self._connectedClient.writeMessage(json.dumps(dict()))
        else:
            super(WSConnectionHandler, self).received_message(message)
