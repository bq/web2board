import json
import logging
import logging.config
import sys

logging.config.dictConfig(json.load(open('logging.json')))
if sys.version_info[0] == 2:
    input = raw_input

# file created by the server
from _static.WSHubsApi import HubsAPI

if __name__ == '__main__':
    ws = HubsAPI('ws://127.0.0.1:8888/')
    ws.connect()

    def printMessage(senderName, message):
        print(u"From {0}: {1}".format(senderName, message))

    ws.ChatHub.client.onMessage = printMessage
    name = input("Enter your name:")
    #ws.server.ChatHub.getNumOfClientsConnected().done(lambda x: sys.stdout.write(x[1]+"\n"), lambda x: sys.stdout.write("Error:%s\n"%x))
    print("Hello %s. You have entered in the chat room, write and press enter to send message" % name)
    while True:
        message = input("")
        if sys.version_info[0] == 2:
            message = message.decode(sys.stdin.encoding)
        ws.ChatHub.server.sendToAll(name, message).done(lambda m: sys.stdout.write("message sent to {} client(s)\n".format(m)),
                                                        lambda m: sys.stdout.write("!!!!!message not sent!!!!! {}\n".format(m)))
