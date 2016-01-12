import importlib
import json
import logging
import logging.config
from wshubsapi.HubsInspector import HubsInspector
from wshubsapi.ConnectionHandlers.WS4Py import ConnectionHandler
from wsgiref.simple_server import make_server
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

logging.config.dictConfig(json.load(open('logging.json')))
log = logging.getLogger(__name__)

if __name__ == '__main__':
    importlib.import_module("ChatHub")  # necessary to add this import for code inspection
    # construct the necessary client files in the specified path
    HubsInspector.inspectImplementedHubs()
    HubsInspector.constructPythonFile("../Clients/_static")
    HubsInspector.constructJSFile("../Clients/_static")
    # Hub.constructJAVAFile("tornado.WSHubsApi", "../Clients/_static")

    server = make_server('127.0.0.1', 8888, server_class=WSGIServer,
                         handler_class=WebSocketWSGIRequestHandler,
                         app=WebSocketWSGIApplication(handler_cls=ConnectionHandler))
    server.initialize_websockets_manager()

    log.debug("starting...")
    target = server.serve_forever()
