import logging
import os

from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WSConnectionHandler(ConnectionHandler):
    def opened(self, *args):
        from libs.MainApp import getMainApp
        self._connectedClient = self.commEnvironment.constructConnectedClient(self.writeMessage, self.close)
        clientId = "Bitbloq"
        self.ID = self._connectedClient.onOpen(clientId)
        log.debug("open new connection with ID: %s " % str(self.ID))
        getMainApp().w2bGui.changeConnectedStatus()

    def closed(self, code, reason=None):
        super(WSConnectionHandler, self).closed(code, reason)