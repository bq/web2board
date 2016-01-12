import json
import logging
import logging.config
import sys

logging.config.dictConfig(json.load(open('logging.json')))
if sys.version_info[0] == 2:
    input = raw_input

# file created by the server
from WSHubsApi import HubsAPI

if __name__ == '__main__':
    ws = HubsAPI('ws://192.168.1.3:8888/')
    ws.connect()

    while True:
        arg = raw_input("writeMessage")
        ws.ChatHub.server.basic(True).done(
            lambda x: sys.stdout.write(str(x)),
            lambda x: sys.stdout.write("error")
        )
