import logging
from datetime import datetime

import time
from PySide.QtCore import QObject
from PySide.QtCore import Signal

from libs.Decorators.Asynchronous import AsynchronousNotDone

__author__ = 'Jorge'


class Result(object):
    def __init__(self):
        self.result = None
        self.startTime = datetime.now()
        self._isDone = False
        self.result = None

    def isDone(self):
        return self._isDone

    def actionDone(self):
        self._isDone = True

    def get(self, joinIfNecessary=True, joinTimeout=None):
        if not self.isDone():
            if joinIfNecessary:
                while not self.isDone() and (joinTimeout is None or joinTimeout <= 0):
                    time.sleep(0.05)
                    if joinTimeout is not None:
                        joinTimeout -= (datetime.now() - self.startTime).seconds
            if not self.isDone():
                raise AsynchronousNotDone("Asynchronous not done yet")
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


# todo, override QObject to work with PyQt too
class InGuiThread(QObject):
    log = logging.getLogger(__name__)
    mainSignal = Signal(object, object)  # *args,**kwargs

    def __init__(self):
        super(InGuiThread, self).__init__()

    def subWrapper(self, args, kwargs):
        """
        Necessary to subWrap because the signal only support a fixed number of arguments
        @param args: the args of the function in a tuple
        @param kwargs: the kwargs of the function in a dict
        @return: the function will not return anything as we have to wait until QT perform the action
        """
        resultObject = kwargs.pop("__resultObject")
        try:
            resultObject.result = self.wrappedFunction(*args, **kwargs)
        except Exception as e:
            self.log.exception("Error in GuiThread")
            resultObject.result = e
        resultObject.actionDone()

    def subSubWrapper(self, *args, **kwargs):
        pass

    def __call__(self, func):
        resultObject = Result()
        self.mainSignal.connect(self.subWrapper)
        self.wrappedFunction = func

        def wrapper(*args, **kwargs):
            kwargs["__resultObject"] = resultObject
            self.mainSignal.emit(args, kwargs)
            return resultObject

        return wrapper
