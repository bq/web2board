import logging
import logging.config
import sys
from WSHubsApi import HubsAPI

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    ws = HubsAPI('ws://172.16.30.105:9876/')
    ws.connect()

    ws.BoardConfigHub.client.isSettingBoard = lambda: sys.stdout.write("is setting BOARD")
    ws.BoardConfigHub.client.isSettingPort = lambda port: sys.stdout.write("is setting PORT: {}".format(port))
    i = 0
    while True:
        board = raw_input("getVersion" if i % 2 == 0 else "getBoard")
        if i % 2 == 0:
            ws.BoardConfigHub.server.getVersion().done(lambda m: sys.stdout.write("\nversion: {}\n".format(m)),
                                                       lambda e: sys.stdout.write("\nerror: {}\n".format(e)))
        else:
            ws.BoardConfigHub.server.setBoard(board).done(lambda m: sys.stdout.write("\nsuccessfully\n"),
                                                          lambda e: sys.stdout.write("\nerror: {}\n".format(e)))
        i += 1
