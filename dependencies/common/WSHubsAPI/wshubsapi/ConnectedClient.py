import logging

from wshubsapi import utils
from wshubsapi.ConnectedClientsHolder import ConnectedClientsHolder
from wshubsapi.FunctionMessage import FunctionMessage

log = logging.getLogger(__name__)


# Change class name //WSAPIClient? WSHUBsClient? ConnHandler?
class ConnectedClient(object):
    def __init__(self, serializationPickler, commEnvironment, writeMessageFunction, closeFunction):
        """
        :type commEnvironment: WSHubsAPI.CommEnvironment.CommEnvironment | None
        """
        self.__commEnvironment = commEnvironment
        self.ID = None
        """:type : int|None|str"""
        self.pickler = serializationPickler
        self.writeMessage = writeMessageFunction
        self.close = closeFunction

    def onOpen(self, ID=None):
        with self.__commEnvironment.lock:
            if ID is None or ID in self.__commEnvironment.allConnectedClients:
                self.ID = self.__commEnvironment.getUnprovidedID()
            else:
                self.ID = ID
            ConnectedClientsHolder.appendClient(self)
            return self.ID

    def onMessage(self, message):
        try:
            msg = FunctionMessage(message, self)
            replay = msg.callFunction()
            if replay is not None:
                self.replay(replay, message)
        except Exception as e:
            self.onError(e)

    def onAsyncMessage(self, message):
        self.__commEnvironment.wsMessageReceivedQueue.put((message, self))

    def onClosed(self):
        ConnectedClientsHolder.popClient(self.ID)

    def onError(self, exception):
        log.exception("Error parsing message")

    def replay(self, replay, originMessage):
        """
        :param replay: serialized object to be sent as a replay of a message received
        :param originMessage: Message received (provided for overridden functions)
        """
        self.writeMessage(utils.serializeMessage(self.pickler, replay))

    def writeMessage(self, message):
        raise NotImplementedError

    def close(self, code, errorMessage):
        raise NotImplementedError
