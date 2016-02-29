import logging
from datetime import datetime
from threading import Thread
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)
__executor = ThreadPoolExecutor(max_workers=25)


class AsynchronousNotDone(Exception):
    pass


# todo, return a Future object and not a Result
class Result(object):
    def __init__(self, future):
        """
        @type thread: Thread
        """
        self.result = None
        self.future = future
        """:type: concurrent.futures._base.Future"""
        self.startTime = datetime.now()

    def isDone(self):
        return self.future.done()

    def get(self, joinTimeout=None):
        if joinTimeout is not None:
            joinTimeout = max([0, joinTimeout - (datetime.now() - self.startTime).seconds])
            self.result = self.future.result(joinTimeout)
        result = self.future.result(joinTimeout)
        if isinstance(result, Exception):
            raise result
        else:
            return result


def asynchronous(daemon=True):
    def realWrapper(fun):
        def overFunction(*args, **kwargs):
            func = kwargs.pop("__func__")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                log.exception("Error in asynchronous task")
                result = e
            return result

        def wrapper(*args, **kwargs):
            kwargs.update({"__func__": fun})
            future = __executor.submit(overFunction, *args, **kwargs)
            resultObject = Result(future)
            kwargs.update({"__ResultObject__": resultObject})
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
