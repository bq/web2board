
import logging
from wshubsapi.connection_handlers.request_handler import TornadoRequestHandler

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RequestHandler(TornadoRequestHandler):
    def __handle_message(self):
        message = self.request.body
        try:
            sort_message = message if len(message) < 500 else message[:300] + "..."
            log.debug("Message received: %s\n%s ", sort_message)
        except UnicodeError:
            pass

        self.comm_environment.on_message(self._connected_client_mock, message)

    def get(self, *args):
        self.__handle_message()


    def post(self):
        self.__handle_message()
