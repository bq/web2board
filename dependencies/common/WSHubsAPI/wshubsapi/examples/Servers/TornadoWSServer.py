import importlib
import os
import logging
import logging.config
import json
from tornado import web, ioloop

from HubsInspector import HubsInspector
from wshubsapi.ConnectionHandlers.Tornado import ConnectionHandler

logging.config.dictConfig(json.load(open('logging.json')))
log = logging.getLogger(__name__)

settings = {"static_path": os.path.join(os.path.dirname(__file__), "../Clients/_static"),}

app = web.Application([
    (r'/(.*)', ConnectionHandler),
], **settings)

if __name__ == '__main__':
    importlib.import_module("ChatHub")  # necessary to add this import for code inspection
    HubsInspector.inspectImplementedHubs()
    HubsInspector.constructJSFile(settings["static_path"])
    HubsInspector.constructPythonFile(settings["static_path"])
    log.debug("starting...")
    app.listen(8888)

    ioloop.IOLoop.instance().start()
