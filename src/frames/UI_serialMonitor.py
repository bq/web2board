# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_serialMonitor.ui'
#
# Created: Fri Feb 19 14:05:57 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_SerialMonitor(object):
    def setupUi(self, SerialMonitor):
        SerialMonitor.setObjectName("SerialMonitor")
        SerialMonitor.resize(519, 529)
        self.centralwidget = QtGui.QWidget(SerialMonitor)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sendLineEdit = QtGui.QLineEdit(self.centralwidget)
        self.sendLineEdit.setObjectName("sendLineEdit")
        self.horizontalLayout.addWidget(self.sendLineEdit)
        self.sendButton = QtGui.QPushButton(self.centralwidget)
        self.sendButton.setObjectName("sendButton")
        self.horizontalLayout.addWidget(self.sendButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.consoleTextEdit = QtGui.QTextEdit(self.centralwidget)
        self.consoleTextEdit.setReadOnly(True)
        self.consoleTextEdit.setObjectName("consoleTextEdit")
        self.verticalLayout.addWidget(self.consoleTextEdit)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pauseButton = QtGui.QPushButton(self.centralwidget)
        self.pauseButton.setCheckable(True)
        self.pauseButton.setObjectName("pauseButton")
        self.horizontalLayout_2.addWidget(self.pauseButton)
        self.clearButton = QtGui.QPushButton(self.centralwidget)
        self.clearButton.setObjectName("clearButton")
        self.horizontalLayout_2.addWidget(self.clearButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setMaxVisibleItems(20)
        self.comboBox.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        SerialMonitor.setCentralWidget(self.centralwidget)

        self.retranslateUi(SerialMonitor)
        self.comboBox.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(SerialMonitor)

    def retranslateUi(self, SerialMonitor):
        SerialMonitor.setWindowTitle(QtGui.QApplication.translate("SerialMonitor", "Serial monitor", None, QtGui.QApplication.UnicodeUTF8))
        self.sendButton.setText(QtGui.QApplication.translate("SerialMonitor", "Send", None, QtGui.QApplication.UnicodeUTF8))
        self.consoleTextEdit.setHtml(QtGui.QApplication.translate("SerialMonitor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.pauseButton.setText(QtGui.QApplication.translate("SerialMonitor", "Pause", None, QtGui.QApplication.UnicodeUTF8))
        self.clearButton.setText(QtGui.QApplication.translate("SerialMonitor", "Clear", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(0, QtGui.QApplication.translate("SerialMonitor", "300", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(1, QtGui.QApplication.translate("SerialMonitor", "1200", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(2, QtGui.QApplication.translate("SerialMonitor", "2400", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(3, QtGui.QApplication.translate("SerialMonitor", "4800", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(4, QtGui.QApplication.translate("SerialMonitor", "9600", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(5, QtGui.QApplication.translate("SerialMonitor", "14400", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(6, QtGui.QApplication.translate("SerialMonitor", "19200", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(7, QtGui.QApplication.translate("SerialMonitor", "28800", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(8, QtGui.QApplication.translate("SerialMonitor", "38400", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(9, QtGui.QApplication.translate("SerialMonitor", "57600", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox.setItemText(10, QtGui.QApplication.translate("SerialMonitor", "115200", None, QtGui.QApplication.UnicodeUTF8))

