import json
import logging
import threading
from threading import Timer
import jsonpickle
from jsonpickle.pickler import Pickler
from ws4py.client.threadedclient import WebSocketClient
from wshubsapi import utils

utils.setSerializerDateTimeHandler()

class WSSimpleObject(object):
    def __setattr__(self, key, value):
        return super(WSSimpleObject, self).__setattr__(key, value)

class WSReturnObject:
    class WSCallbacks:
        def __init__(self, onSuccess=None, onError=None):
            self.onSuccess = onSuccess
            self.onError = onError

    def done(self, onSuccess, onError=None):
        pass

class GenericServer(object):
    __messageID = 0
    __messageLock = threading.RLock()

    def __init__(self, wsClient, hubName, pickler):
        """
        :type wsClient: WSHubsAPIClient
        """
        self.wsClient = wsClient
        self.hubName = hubName
        self.pickler = pickler

    @classmethod
    def _getNextMessageID(cls):
        with cls.__messageLock:
            cls.__messageID += 1
            return cls.__messageID

    def _serializeObject(self, obj2ser):
        return jsonpickle.encode(self.pickler.flatten(obj2ser))


class WSHubsAPIClient(WebSocketClient):
    def __init__(self, api, url, serverTimeout):
        super(WSHubsAPIClient, self).__init__(url)
        self.__returnFunctions = dict()
        self.isOpened = False
        self.serverTimeout = serverTimeout
        self.api = api
        self.log = logging.getLogger(__name__)
        self.log.addHandler(logging.NullHandler())

    def opened(self):
        self.isOpened = True
        self.log.debug("Connection opened")

    def closed(self, code, reason=None):
        self.log.debug("Connection closed with code:\n%s\nAnd reason:\n%s" % (code, reason))

    def received_message(self, m):
        try:
            msgObj = json.loads(m.data.decode('utf-8'))
        except Exception as e:
            self.onError(e)
            return
        if "replay" in msgObj:
            f = self.__returnFunctions.get(msgObj["ID"], None)
            if f and msgObj["success"]:
                f.onSuccess(msgObj["replay"])
            elif f and f.onError:
                f.onError(msgObj["replay"])
        else:
            self.api.__getattribute__(msgObj["hub"]).client.__dict__[msgObj["function"]](*msgObj["args"])
        self.log.debug("Received message: %s" % m.data.decode('utf-8'))

    def getReturnFunction(self, ID):
        """
        :rtype : WSReturnObject
        """

        def returnFunction(onSuccess, onError=None):
            callBacks = self.__returnFunctions.get(ID, WSReturnObject.WSCallbacks())

            def onSuccessWrapper(*args, **kwargs):
                onSuccess(*args, **kwargs)
                self.__returnFunctions.pop(ID, None)

            callBacks.onSuccess = onSuccessWrapper
            if onError is not None:
                def onErrorWrapper(*args, **kwargs):
                    onError(*args, **kwargs)
                    self.__returnFunctions.pop(ID, None)

                callBacks.onError = onErrorWrapper
            else:
                callBacks.onError = None
            self.__returnFunctions[ID] = callBacks
            r = Timer(self.serverTimeout, self.onTimeOut, (ID,))
            r.start()

        retObject = WSReturnObject()
        retObject.done = returnFunction

        # todo create timeout
        return retObject

    def onError(self, exception):
        self.log.exception("Error in protocol")

    def onTimeOut(self, messageId):
        f = self.__returnFunctions.pop(messageId, None)
        if f and f.onError:
            f.onError("timeOut Error")

class HubsAPI(object):
    def __init__(self, url, serverTimeout=5.0, pickler=Pickler(max_depth=4, max_iter=100, make_refs=False)):
        self.wsClient = WSHubsAPIClient(self, url, serverTimeout)
        self.pickler = pickler
        self.BaseHub = self.__BaseHub(self.wsClient, self.pickler)

    def connect(self):
        self.wsClient.connect()


    class __BaseHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def sendToAll(self, name, message):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(name)
                args.append(message)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "sendToAll", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def timeout(self, timeout=3):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(timeout)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "timeout", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
