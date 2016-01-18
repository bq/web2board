import logging
from datetime import datetime
from threading import Thread

import threading

log = logging.getLogger(__name__)

class AsynchronousNotDone(Exception):
    pass


class Result(object):
    def __init__(self, thread):
        """
        @type thread: Thread
        """
        self.result = None
        self.thread = thread
        self.startTime = datetime.now()

    def isDone(self):
        return not self.thread.isAlive()

    def get(self, joinIfNecessary=True, joinTimeout=None):
        if not self.isDone():
            if joinIfNecessary:
                realTimeout = max([0, joinTimeout-(datetime.now() - self.startTime).seconds])
                self.thread.join(realTimeout)
            else:
                raise AsynchronousNotDone("Asynchronous not done yet")
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def asynchronous(callback=None, callbackArgs=(), callbackKwargs=None, daemon=True):
    if callbackKwargs is None:
        callbackKwargs = {}

    def realWrapper(fun):
        def overFunction(*args, **kwargs):
            func = kwargs.pop("__func__")
            resultObject = kwargs.pop("__ResultObject__")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                log.exception("Error in asynchronous task")
                result = e
            resultObject.result = result
            if callback is not None:
                callback(result, *callbackArgs, **callbackKwargs)

        def wrapper(*args, **kwargs):
            kwargs.update({"__func__": fun})
            _mainThread = threading.Thread(target=overFunction, args=args, kwargs=kwargs)
            _mainThread.setDaemon(daemon)
            resultObject = Result(_mainThread)
            _mainThread.functionsArgs = args
            kwargs.update({"__ResultObject__": resultObject})
            _mainThread.functionKwargs = kwargs
            _mainThread.start()
            return resultObject

        return wrapper

    return realWrapper

# # EXAMPLE
# import time
#
#
# def callb(value):
#     print "calback"
#     print value
#
#
# @asynchronous(callb)
# def timer(delay):
#     print "starting"
#     time.sleep(delay)
#     print "finished"
#     return "resultValue"
#
#
# res = timer(5)
# print "after async"
# print "waiting timer to finish with value %s" % res.get()
