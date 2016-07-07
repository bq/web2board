import logging

from bottle import Bottle, request, run, response
from wshubsapi.comm_environment import CommEnvironment
from wshubsapi.connected_client import ConnectedClient

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

app = Bottle()

@app.hook('after_request')
def enable_cors():
    print "after_request hook"
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'



@app.post('/')
def handle_message():
    comm_environment = CommEnvironment.get_instance()
    message = ""

    def on_message(msg):
        global message
        message = msg

    connected_client_mock = ConnectedClient(comm_environment, on_message)

    return message


def start(options):
    run(app, host=options.host, port=options.port)