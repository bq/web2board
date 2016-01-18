# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\SoftwareProjects\web2board\src\frames\UI_web2board.ui'
#
# Created: Sun Jan 17 18:27:48 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Web2board(object):
    def setupUi(self, Web2board):
        Web2board.setObjectName("Web2board")
        Web2board.resize(825, 417)
        self.centralwidget = QtGui.QWidget(Web2board)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.ports = QtGui.QComboBox(self.centralwidget)
        self.ports.setMinimumSize(QtCore.QSize(100, 0))
        self.ports.setObjectName("ports")
        self.ports.addItem("")
        self.horizontalLayout.addWidget(self.ports)
        self.searchPorts = QtGui.QPushButton(self.centralwidget)
        self.searchPorts.setObjectName("searchPorts")
        self.horizontalLayout.addWidget(self.searchPorts)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.console = QtGui.QTextEdit(self.centralwidget)
        self.console.setReadOnly(True)
        self.console.setObjectName("console")
        self.verticalLayout_2.addWidget(self.console)
        Web2board.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(Web2board)
        self.statusbar.setObjectName("statusbar")
        Web2board.setStatusBar(self.statusbar)

        self.retranslateUi(Web2board)
        QtCore.QMetaObject.connectSlotsByName(Web2board)

    def retranslateUi(self, Web2board):
        Web2board.setWindowTitle(QtGui.QApplication.translate("Web2board", "Web2board", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Web2board", "ports:", None, QtGui.QApplication.UnicodeUTF8))
        self.ports.setItemText(0, QtGui.QApplication.translate("Web2board", "AUTO", None, QtGui.QApplication.UnicodeUTF8))
        self.searchPorts.setText(QtGui.QApplication.translate("Web2board", "Search ports", None, QtGui.QApplication.UnicodeUTF8))

