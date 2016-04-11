import json
import logging
import threading
from threading import Timer
import jsonpickle
from jsonpickle.pickler import Pickler
from wshubsapi import utils

utils.setSerializerDateTimeHandler()
_defaultPickler = Pickler(max_depth=4, max_iter=100, make_refs=False)


class WSSimpleObject(object):
    def __setattr__(self, key, value):
        return super(WSSimpleObject, self).__setattr__(key, value)


class WSReturnObject:
    class WSCallbacks:
        def __init__(self, onSuccess=None, onError=None):
            self.onSuccess = onSuccess
            self.onError = onError
            self.onFinally = lambda: None

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


def constructAPIClientClass(clientClass):
    if clientClass is None:
        from ws4py.client.threadedclient import WebSocketClient
        clientClass = WebSocketClient
    class WSHubsAPIClient(clientClass):
        def __init__(self, api, url, serverTimeout):
            """
            :type api: HubsAPI
            """
            clientClass.__init__(self, url)
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
                try:
                    if f and msgObj["success"]:
                        f.onSuccess(msgObj["replay"])
                    elif f and f.onError:
                        f.onError(msgObj["replay"])
                finally:
                    if f:
                        f.onFinally()
            else:
                try:
                    clientFunction = self.api.__getattribute__(msgObj["hub"]).client.__dict__[msgObj["function"]]
                    replayMessage = dict(ID=msgObj["ID"])
                    try:
                        replay = clientFunction(*msgObj["args"])
                        replayMessage["replay"] = replay
                        replayMessage["success"] = True
                    except Exception as e:
                        replayMessage["replay"] = str(e)
                        replayMessage["success"] = False
                    finally:
                        self.api.wsClient.send(self.api.serializeObject(replayMessage))
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
                return callBacks

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

    return WSHubsAPIClient


class HubsAPI(object):
    def __init__(self, url, serverTimeout=5.0, clientClass=None, pickler=_defaultPickler):
        apiClientClass = constructAPIClientClass(clientClass)
        self.wsClient = apiClientClass(self, url, serverTimeout)
        self.wsClient.defaultOnError = lambda error: None
        self.pickler = pickler
        self.CodeHub = self.__CodeHub(self.wsClient, self.pickler)
        self.VersionsHandlerHub = self.__VersionsHandlerHub(self.wsClient, self.pickler)
        self.LoggingHub = self.__LoggingHub(self.wsClient, self.pickler)
        self.WindowHub = self.__WindowHub(self.wsClient, self.pickler)
        self.UtilsAPIHub = self.__UtilsAPIHub(self.wsClient, self.pickler)
        self.SerialMonitorHub = self.__SerialMonitorHub(self.wsClient, self.pickler)
        self.ConfigHub = self.__ConfigHub(self.wsClient, self.pickler)

    @property
    def defaultOnError(self):
        return None

    @defaultOnError.setter
    def defaultOnError(self, func):
        self.wsClient.defaultOnError = func

    def connect(self):
        self.wsClient.connect()

    def serializeObject(self, obj2ser):
        return jsonpickle.encode(self.pickler.flatten(obj2ser))


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
        
            def getHexData(self, code):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(code)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getHexData", "args": args, "ID": id}
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
        
            def upload(self, code, board, port=None):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(code)
                args.append(board)
                args.append(port)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "upload", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def uploadHex(self, hexText, board, port=None):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(hexText)
                args.append(board)
                args.append(port)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "uploadHex", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def uploadHexFile(self, hexFilePath, board, port=None):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(hexFilePath)
                args.append(board)
                args.append(port)
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
        
    class __LoggingHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def getAllBufferedRecords(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getAllBufferedRecords", "args": args, "ID": id}
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
        
    class __WindowHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def forceClose(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "forceClose", "args": args, "ID": id}
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
        
            def closeAllConnections(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "closeAllConnections", "args": args, "ID": id}
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
        
            def findBoardPort(self, board):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(board)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "findBoardPort", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getAllConnectedPorts(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getAllConnectedPorts", "args": args, "ID": id}
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
        
    class __ConfigHub(object):
        def __init__(self, wsClient, pickler):
            hubName = self.__class__.__name__[2:]
            self.server = self.__Server(wsClient, hubName, pickler)
            self.client = WSSimpleObject()

        class __Server(GenericServer):
            
            def changePlatformioIniFile(self, content):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(content)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "changePlatformioIniFile", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getConfig(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getConfig", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def getLibrariesPath(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "getLibrariesPath", "args": args, "ID": id}
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
        
            def isPossibleLibrariesPath(self, path):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(path)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "isPossibleLibrariesPath", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def restorePlatformioIniFile(self, ):
                """
                :rtype : WSReturnObject
                """
                args = list()
                
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "restorePlatformioIniFile", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setLibrariesPath(self, libDir):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(libDir)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setLibrariesPath", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setLogLevel(self, logLevel):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(logLevel)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setLogLevel", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setProxy(self, proxyUrl):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(proxyUrl)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setProxy", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setValues(self, configDic):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(configDic)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setValues", "args": args, "ID": id}
                retFunction = self.wsClient.getReturnFunction(id)
                self.wsClient.send(self._serializeObject(body))
                return retFunction
        
            def setWebSocketInfo(self, IP, port):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(IP)
                args.append(port)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "setWebSocketInfo", "args": args, "ID": id}
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
        
            def testProxy(self, proxyUrl):
                """
                :rtype : WSReturnObject
                """
                args = list()
                args.append(proxyUrl)
                id = self._getNextMessageID()
                body = {"hub": self.hubName, "function": "testProxy", "args": args, "ID": id}
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
        