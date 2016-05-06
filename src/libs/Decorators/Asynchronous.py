import logging
from concurrent.futures import ThreadPoolExecutor

log = logging.getLogger(__name__)
__executor = ThreadPoolExecutor(max_workers=25)


def asynchronous():
    def real_wrapper(fun):
        def over_function(*args, **kwargs):
            func = kwargs.pop("__func__")
            return func(*args, **kwargs)

        def wrapper(*args, **kwargs):
            kwargs.update({"__func__": fun})
            return __executor.submit(over_function, *args, **kwargs)


        return wrapper

    return real_wrapper

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
