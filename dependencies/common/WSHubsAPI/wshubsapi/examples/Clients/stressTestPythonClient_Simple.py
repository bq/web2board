# Execute as many times as required in parallel

import json
import logging
import logging.config
import sys
import time

logging.config.dictConfig(json.load(open('logging.json')))
if sys.version_info[0] == 2:
    input = raw_input

from threading import Lock

lock = Lock()

receivedFromServerCount = 0
receivedMessagesCount = 0
sentMessagesCount = 0
errorsCount = 0

# file created by the server
from _static.WSHubsApi import HubsAPI


def printMessage(senderName, message):
    global receivedFromServerCount
    with lock:
        receivedFromServerCount += 1


def singleAction(index):
    ws = HubsAPI('ws://127.0.0.1:8888/')
    ws.connect()

    ws.ChatHub.client.onMessage = printMessage
    name = "jorge {}".format(index)
    for i in range(3):
        time.sleep(0.03)
        message = "message {}".format(i)
        ws.ChatHub.server.sendToAll(name, message).done(
            lambda m: sys.stdout.write("message sent to %d client(s)\n" % m),
            lambda m: sys.stdout.write(str(m)))


def receivedMessage(message):
    global receivedMessagesCount
    receivedMessagesCount += 1
    print(receivedMessagesCount)


def receivedError(error):
    print(error)
    global errorsCount
    errorsCount += 1


if __name__ == '__main__':
    connections = []
    for i in range(5):
        connections.append(HubsAPI('ws://127.0.0.1:8888/'))
        connections[-1].connect()
        connections[-1].ChatHub.client.onMessage = printMessage
    print("starting...")
    for j in range(1000):
        for i, conn in enumerate(connections):
            conn.ChatHub.server.sendToAll(str(i), "message {}".format(i)).done(
                receivedMessage,
                receivedError)
            sentMessagesCount += 1
            time.sleep(0.006)  # play with this value because it is possible to reach threads limit

    print("end")
    time.sleep(1)
    print([receivedMessagesCount, receivedFromServerCount, sentMessagesCount, errorsCount])
    time.sleep(100)
