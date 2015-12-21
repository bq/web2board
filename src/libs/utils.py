import inspect
import os
import sys


def areWeFrozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")

def getModulePath(frame = None):
    encoding = sys.getfilesystemencoding()
    encoding = encoding if encoding is not None else 'utf-8'
    if not areWeFrozen():
        frame = frame if frame is not None else inspect.currentframe().f_back
        info = inspect.getframeinfo(frame)
        fileName = info.filename
        return os.path.dirname(os.path.abspath(unicode(fileName, encoding)))
    else:
        return os.path.dirname(os.path.abspath(unicode(sys.executable, encoding)))