import os
import sys
import time


def main():
    fh = open('log', 'a')
    while True:
        fh.write('Still alive!')
        fh.flush()
        time.sleep(1)


def _fork():
    try:
        pid = os.fork()
        if pid > 0:
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, 'Unable to fork: %d (%s)' % (e.errno, e.strerror)
        sys.exit(1)


def fork():
    _fork()

    # remove references from the main process
    os.chdir('/')
    os.setsid()
    os.umask(0)

    _fork()




import sys
from PySide.QtGui import *

if __name__ == '__main__':
    app = QApplication(sys.argv)

    widget = QWidget()

    mainWindow = QMainWindow(widget)
    mainWindow.show()

    sys.exit(app.exec_())