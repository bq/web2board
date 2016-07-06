import logging
from SimpleHTTPServer import SimpleHTTPRequestHandler

from wshubsapi.comm_environment import CommEnvironment
from wshubsapi.connected_client import ConnectedClient
from wshubsapi.connection_handlers.request_handler import SimpleRequestHandler

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RequestHandler(SimpleRequestHandler):
    def setup(self):
        SimpleHTTPRequestHandler.setup(self)
        self.comm_environment = CommEnvironment.get_instance()
        self._connected_client_mock = ConnectedClient(self.comm_environment, self.write_message)

    def write_message(self, message):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(message)
        self.wfile.close()

    def __get_body(self):
        content_len = int(self.headers.getheader('content-length', 0))
        return self.rfile.read(content_len)

    def __handle_message(self):
        message = self.__get_body()
        try:
            sort_message = message if len(message) < 500 else message[:300] + "..."
            log.debug("Message received: \n%s ", sort_message)
        except UnicodeError:
            pass

        self.comm_environment.on_message(self._connected_client_mock, message)

    def do_POST(self, *args):
        self.__handle_message()