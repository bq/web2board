import logging

from bottle import Bottle, request, run, response
from wshubsapi.comm_environment import CommEnvironment
from wshubsapi.connected_client import ConnectedClient

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

app = Bottle()


# the decorator
def enable_cors(fn):
    def _enable_cors(*args, **kwargs):
        # set CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, x-requested-with'

        if request.method != 'OPTIONS':
            # actual request; reply with the actual response
            return fn(*args, **kwargs)

    return _enable_cors


@app.route('/', method=['OPTIONS', 'POST'])
@enable_cors
def handle_message():
    comm_environment = CommEnvironment.get_instance()
    message = request.body.buf
    replay_holder = dict()

    def on_message(msg):
        replay_holder["msg"] = msg

    connected_client_mock = ConnectedClient(comm_environment, on_message)
    comm_environment.on_message(connected_client_mock, message)

    return replay_holder["msg"]


def start(options):
    run(app, host=options.host, port=options.port)