# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_web2board.ui'
#
# Created: Wed Jan 27 09:27:04 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Web2board(object):
    def setupUi(self, Web2board):
        Web2board.setObjectName("Web2board")
        Web2board.resize(838, 431)
        self.centralwidget = QtGui.QWidget(Web2board)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.forceClose = QtGui.QPushButton(self.centralwidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.forceClose.setIcon(icon)
        self.forceClose.setObjectName("forceClose")
        self.horizontalLayout.addWidget(self.forceClose)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.wsConnectedLabel = QtGui.QLabel(self.centralwidget)
        self.wsConnectedLabel.setObjectName("wsConnectedLabel")
        self.horizontalLayout.addWidget(self.wsConnectedLabel)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
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
        self.updateGroupbox = QtGui.QGroupBox(self.centralwidget)
        self.updateGroupbox.setObjectName("updateGroupbox")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.updateGroupbox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.progressBar = QtGui.QProgressBar(self.updateGroupbox)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)
        self.info = QtGui.QLabel(self.updateGroupbox)
        self.info.setObjectName("info")
        self.verticalLayout_3.addWidget(self.info)
        self.verticalLayout_2.addWidget(self.updateGroupbox)
        Web2board.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(Web2board)
        self.statusbar.setObjectName("statusbar")
        Web2board.setStatusBar(self.statusbar)

        self.retranslateUi(Web2board)
        QtCore.QMetaObject.connectSlotsByName(Web2board)

    def retranslateUi(self, Web2board):
        Web2board.setWindowTitle(QtGui.QApplication.translate("Web2board", "Web2board", None, QtGui.QApplication.UnicodeUTF8))
        self.forceClose.setText(QtGui.QApplication.translate("Web2board", "Force close", None, QtGui.QApplication.UnicodeUTF8))
        self.wsConnectedLabel.setText(QtGui.QApplication.translate("Web2board", "Not connected", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Web2board", "ports:", None, QtGui.QApplication.UnicodeUTF8))
        self.ports.setItemText(0, QtGui.QApplication.translate("Web2board", "AUTO", None, QtGui.QApplication.UnicodeUTF8))
        self.searchPorts.setText(QtGui.QApplication.translate("Web2board", "Search ports", None, QtGui.QApplication.UnicodeUTF8))
        self.updateGroupbox.setTitle(QtGui.QApplication.translate("Web2board", "Downloading", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setText(QtGui.QApplication.translate("Web2board", "Info:", None, QtGui.QApplication.UnicodeUTF8))

