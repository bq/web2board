#!/usr/bin/env python
# coding=utf-8
import sys

from PySide import QtGui

from frames.LinuxInstallerWindow import LinuxInstallerWindow

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mySW = LinuxInstallerWindow(None)
    mySW.show()
    sys.exit(app.exec_())