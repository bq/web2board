# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_Updater.ui'
#
# Created: Thu Jan 21 09:56:40 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Updater(object):
    def setupUi(self, Updater):
        Updater.setObjectName("Updater")
        Updater.resize(483, 80)
        Updater.setWindowOpacity(1.0)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Updater)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.title = QtGui.QLabel(Updater)
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setWeight(75)
        font.setBold(True)
        self.title.setFont(font)
        self.title.setObjectName("title")
        self.verticalLayout.addWidget(self.title)
        self.progressBar = QtGui.QProgressBar(Updater)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.info = QtGui.QLabel(Updater)
        self.info.setObjectName("info")
        self.verticalLayout.addWidget(self.info)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Updater)
        QtCore.QMetaObject.connectSlotsByName(Updater)

    def retranslateUi(self, Updater):
        Updater.setWindowTitle(QtGui.QApplication.translate("Updater", "Updater", None, QtGui.QApplication.UnicodeUTF8))
        self.title.setText(QtGui.QApplication.translate("Updater", "Updating from", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setText(QtGui.QApplication.translate("Updater", "Info:", None, QtGui.QApplication.UnicodeUTF8))

