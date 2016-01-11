import inspect
from sys import stdout

import wx


class EventInfo:
    def __init__(self):
        self.eventType = wx.NewEventType()
        self.event = wx.PyEventBinder(self.eventType, 1)


class WX_Utils:
    functionsOnGuiThread = list()
    eventsInfo = dict()
    myEVT_COUNT = wx.NewEventType()
    EVT_COUNT = wx.PyEventBinder(myEVT_COUNT, 1)

    def __init__(self):
        pass

    @classmethod
    def initDecorators(cls, frame):
        """
        :type frame: wx.Frame
        """
        frameMembers = inspect.getmembers(frame.__class__)
        functionNamesOnGuiThread = map(lambda x: x.func_name, cls.functionsOnGuiThread)
        functions = []
        for f in frameMembers:
            try:
                index = functionNamesOnGuiThread.index(f[0])
                functions.append([f[0], cls.functionsOnGuiThread[index]])
            except:
                pass

        for f in functions:
            eventInfo = EventInfo()
            cls.eventsInfo[cls.getKey(frame, f[0])] = eventInfo
            frame.Bind(eventInfo.event, lambda x: f[1](frame, *x.args, **x.kwargs))

    @classmethod
    def onGuiThread(cls):
        def realWrapper(fun):
            cls.functionsOnGuiThread.append(fun)

            def wrapper(frame, *args, **kwargs):
                event = wx.PyCommandEvent(cls.getEventInfo(frame, fun.func_name).eventType, -1)
                event.args = args
                event.kwargs = kwargs
                wx.PostEvent(frame, event)

            return wrapper

        return realWrapper

    @classmethod
    def getEventInfo(cls, frame, funName):
        return cls.eventsInfo[cls.getKey(frame, funName)]

    @classmethod
    def getKey(cls, frame, funName):
        return frame.__class__.__name__ + "_" + funName

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
