from PySide.QtCore import QObject
from PySide.QtCore import Signal


__author__ = 'Jorge'

#todo, override QObject to work with PyQt too
#todo, add a way to allow return values
class InGuiThread(QObject):
    mainSignal=Signal(object, object)#*args,**kwargs
    def __init__(self):
        super(InGuiThread, self).__init__()

    def subWrapper(self, args, kwargs):
        """
        Necessary to subWrap because the signal only support a fixed number of arguments
        @param args: the args of the function in a tuple
        @param kwargs: the kwargs of the function in a dict
        @return: the function will not return anything as we have to wait until QT perform the action
        """
        self.wrappedFunction(*args,**kwargs)

    def subSubWrapper(self,*args,**kwargs):
        pass

    def __call__(self, func):
        self.mainSignal.connect(self.subWrapper)
        self.wrappedFunction=func
        def wrapper(*args, **kwargs):
            self.mainSignal.emit(args,kwargs)
        return wrapper