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
            try:
                clientFunction = self.api.__getattribute__(msgObj["hub"]).client.__dict__[msgObj["function"]]
                clientFunction(*msgObj["args"])
            except:
                pass


        self.log.debug("Received message: %s" % m.data.decode('utf-8'))

    def getReturnFunction(self, ID):
        """
        :rtype : WSReturnObject
        """

        def returnFunction(onSuccess, onError=None, timeOut=None):
            callBacks = self.__returnFunctions.get(ID, WSReturnObject.WSCallbacks())
            onError = onError if onError is not None else self.defaultOnError

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

            timeOut = timeOut if timeOut is not None else self.serverTimeout
            r = Timer(timeOut, self.onTimeOut, (ID,))
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

    def defaultOnError(self, error):
        pass

class HubsAPI(object):
    def __init__(self, url, serverTimeout=5.0, pickler=Pickler(max_depth=4, max_iter=100, make_refs=False)):
        self.wsClient = WSHubsAPIClient(self, url, serverTimeout)
        self.wsClient.defaultOnError = lambda error: None
        self.pickler = pickler
        self.UtilsAPIHub = self.__UtilsAPIHub(self.wsClient, self.pickler)
        self.CodeHub = self.__CodeHub(self.wsClient, self.pickler)
        self.VersionsHandlerHub = self.__VersionsHandlerHub(self.wsClient, self.pickler)
        self.SerialMonitorHub = self.__SerialMonitorHub(self.wsClient, self.pickler)

    @property
    def defaultOnError(self):
        return None

    @defaultOnError.setter
    def defaultOnError(self, func):
        self.wsClient.defaultOnError = func

    def connect(self):
        self.wsClient.connect()


    class __UtilsAPIHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def getHubsStructure(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getHubsStructure", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getId(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getId", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getSubscribedClientsToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getSubscribedClientsToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def isClientConnected(self, clientId):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(clientId)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "isClientConnected", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setId(self, clientId):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(clientId)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setId", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def subscribeToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "subscribeToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def unsubscribeFromHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "unsubscribeFromHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __CodeHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def compile(self, code):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(code)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "compile", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getSubscribedClientsToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getSubscribedClientsToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def subscribeToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "subscribeToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def tryToTerminateSerialCommProcess(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "tryToTerminateSerialCommProcess", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def unsubscribeFromHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "unsubscribeFromHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def upload(self, code, board):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(code)
                args.append(board)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "upload", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def uploadHex(self, hexText, board):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(hexText)
                args.append(board)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "uploadHex", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def uploadHexFile(self, hexFilePath, board):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(hexFilePath)
                args.append(board)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "uploadHexFile", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __VersionsHandlerHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def getSubscribedClientsToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getSubscribedClientsToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getVersion(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getVersion", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setLibVersion(self, version):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(version)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setLibVersion", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setWeb2boardVersion(self, version):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(version)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setWeb2boardVersion", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def subscribeToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "subscribeToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def unsubscribeFromHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "unsubscribeFromHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
    class __SerialMonitorHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def changeBaudrate(self, port, baudrate):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                args.append(baudrate)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "changeBaudrate", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def closeConnection(self, port):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "closeConnection", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def findBoardPort(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "findBoardPort", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getAvailablePorts(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getAvailablePorts", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getSubscribedClientsToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getSubscribedClientsToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def isPortConnected(self, port):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "isPortConnected", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def startApp(self, port, board):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                args.append(board)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "startApp", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def startConnection(self, port, baudrate=9600):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                args.append(baudrate)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "startConnection", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def subscribeToHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "subscribeToHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def unsubscribeFromHub(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "unsubscribeFromHub", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def write(self, port, data):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(port)
                args.append(data)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "write", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
