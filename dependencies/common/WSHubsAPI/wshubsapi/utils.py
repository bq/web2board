import jsonpickle

try:
    from Queue import Queue
except:
    from queue import Queue

import datetime
import inspect
import os
import string
import sys
from inspect import getargspec
from concurrent.futures import ThreadPoolExecutor
from jsonpickle import handlers

SENDER_KEY_PARAMETER = "_sender"
DATE_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f%z'
NOT_PASSING_PARAMETERS = (SENDER_KEY_PARAMETER,)

try:
    textTypes = [str, unicode]
except:
    textTypes = [str, bytes]
ASCII_UpperCase = string.uppercase if sys.version_info[0] == 2 else string.ascii_uppercase


def getArgs(method, includeSender=False):
    args = getargspec(method).args
    if args is None: return []
    if hasattr(method, "__self__"):
        args.pop(0)
    if not includeSender:
        for arg in NOT_PASSING_PARAMETERS:
            try:
                args.remove(arg)
            except:
                pass
    return args


def getDefaults(method):
    d = getargspec(method).defaults
    if d is None: return []
    d = list(filter(lambda x: x not in NOT_PASSING_PARAMETERS, list(d)))
    for i in range(len(d)):
        if isinstance(d[i], tuple(textTypes)):
            d[i] = '"%s"' % d[i]
    return d


def isFunctionForWSClient(method):
    from wshubsapi.Hub import Hub
    isFunction = lambda x: inspect.ismethod(x) or inspect.isfunction(x)
    BaseHubFunctions = inspect.getmembers(Hub, predicate=isFunction)
    BaseHubFunctionsNames = [f[0] for f in BaseHubFunctions]

    return isFunction(method) and not method.__name__.startswith("_") and method.__name__ not in BaseHubFunctionsNames


def getModulePath():
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)
    fileName = info.filename
    return os.path.dirname(os.path.abspath(fileName))


# todo: move to different module
class WSMessagesReceivedQueue(Queue):
    DEFAULT_MAX_WORKERS = 151

    def __init__(self, maxWorkers=DEFAULT_MAX_WORKERS):
        Queue.__init__(self)
        self.maxWorkers = maxWorkers
        self.executor = ThreadPoolExecutor(max_workers=self.maxWorkers)
        self.keepAlive = True

    def startThreads(self):
        for i in range(self.DEFAULT_MAX_WORKERS):
            self.executor.submit(self.__infiniteOnMessageHandlerLoop)

    def __infiniteOnMessageHandlerLoop(self):
        while self.keepAlive:
            connectedClient = None
            try:
                msg, connectedClient = self.get()
                connectedClient.onMessage(msg)
            except Exception as e:
                if connectedClient is not None:
                    connectedClient.onError(e)
                else:
                    print(str(e))  # todo: create a call back for this exception


def setSerializerDateTimeHandler():
    class WSDateTimeObjects(handlers.BaseHandler):
        def restore(self, obj):
            pass

        def flatten(self, obj, data):
            return obj.strftime(DATE_TIME_FORMAT)

    handlers.register(datetime.datetime, WSDateTimeObjects)
    handlers.register(datetime.date, WSDateTimeObjects)
    handlers.register(datetime.time, WSDateTimeObjects)


def serializeMessage(serializationPickler, message):
    return jsonpickle.encode(serializationPickler.flatten(message))
