import json
import logging

from wshubsapi.ConnectedClientsGroup import ConnectedClientsGroup
from wshubsapi.ConnectedClientsHolder import ConnectedClientsHolder
from wshubsapi.utils import getArgs, SENDER_KEY_PARAMETER
from wshubsapi.Hub import Hub, UnsuccessfulReplay

log = logging.getLogger(__name__)


class FunctionMessage:
    def __init__(self, messageStr, connectedClient):
        """
        :type messageStr: bytes|str
        """
        messageStr = messageStr if isinstance(messageStr, str) else messageStr.decode("utf-8")
        msgObj = json.loads(messageStr)
        self.hubInstance = Hub.HUBs_DICT[msgObj["hub"]]
        self.hubName = msgObj["hub"]
        self.args = msgObj["args"]
        self.connectedClient = connectedClient

        self.functionName = msgObj["function"]
        self.method = getattr(self.hubInstance, self.functionName)
        self.messageID = msgObj.get("ID", -1)

    def __executeFunction(self):
        try:
            self.__includeSenderInArgs(self.method, self.args)
            return True, self.method(*self.args)
        except Exception as e:
            log.exception("Error calling hub function")
            return False, str(e)

    def callFunction(self):
        success, replay = self.__executeFunction()
        if isinstance(replay, UnsuccessfulReplay):
            return self.constructReplayDict(False, replay.replay)
        if replay is not None:
            return self.constructReplayDict(success, replay)

    def constructReplayDict(self, success=None, replay=None):
        return {
            "success": success,
            "replay": replay,
            "hub": self.hubName,
            "function": self.functionName,
            "ID": self.messageID
        }

    def __includeSenderInArgs(self, method, args):
        """
        :type args: list
        """
        methodArgs = getArgs(method, includeSender=True)
        try:
            senderIndex = methodArgs.index(SENDER_KEY_PARAMETER)
            args.insert(senderIndex, ConnectedClientsGroup([self.connectedClient], self.hubName))
        except ValueError:
            pass
