import json
import logging
import os
import time
from wshubsapi.connection_handlers.tornado_handler import ConnectionHandler

import libs.MainApp
from libs import utils
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class WSConnectionHandler(ConnectionHandler):
    def open(self, *args):
        super(WSConnectionHandler, self).open(*args)

    def on_close(self):
        super(WSConnectionHandler, self).on_close()
        if self._connected_client.ID == "Bitbloq":
            log.info("Bitbloq disconnected, closing web2board...")
            time.sleep(0.5)
            if utils.are_we_frozen():
                libs.MainApp.forceQuit()

    def on_message(self, message):
        if message == "version":  # bitbloq thinks we are in version 1
            # send an empty dict to alert bitbloq we are in version 2
            self._connected_client.api_write_message(json.dumps(dict()))
        else:
            try:
                sortMessage = message if len(message) < 500 else message[:300] + "..."
                log.debug("Message received from ID: %s\n%s " % (str(self._connected_client.ID), sortMessage))
            except UnicodeError:
                pass
            self.comm_environment.on_async_message(self._connected_client, message.encode('utf-8', 'ignore'))
