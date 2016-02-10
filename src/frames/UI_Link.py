# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_Link.ui'
#
# Created: Tue Feb 09 12:41:16 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Link(object):
    def setupUi(self, Link):
        Link.setObjectName("Link")
        Link.resize(462, 135)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Link)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loading = QtGui.QLabel(Link)
        self.loading.setText("")
        self.loading.setObjectName("loading")
        self.horizontalLayout.addWidget(self.loading)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtGui.QLabel(Link)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.label_2 = QtGui.QLabel(Link)
        font = QtGui.QFont()
        font.setWeight(50)
        font.setBold(False)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_3.addWidget(self.label_2)
        self.status = QtGui.QLabel(Link)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setWeight(75)
        font.setBold(True)
        self.status.setFont(font)
        self.status.setText("")
        self.status.setObjectName("status")
        self.verticalLayout_3.addWidget(self.status)
        self.verticalLayout_3.setStretch(2, 1)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.tryAgain = QtGui.QPushButton(Link)
        self.tryAgain.setObjectName("tryAgain")
        self.horizontalLayout_2.addWidget(self.tryAgain)
        self.close = QtGui.QPushButton(Link)
        self.close.setEnabled(False)
        self.close.setCheckable(True)
        self.close.setObjectName("close")
        self.horizontalLayout_2.addWidget(self.close)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Link)
        QtCore.QObject.connect(self.close, QtCore.SIGNAL("clicked()"), Link.accept)
        QtCore.QMetaObject.connectSlotsByName(Link)

    def retranslateUi(self, Link):
        Link.setWindowTitle(QtGui.QApplication.translate("Link", "Web2boardLink", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Link", "Web2board is configuring some files.\n"
"This can take a while but it will be done just once.\n"
"If this process takes more than 5 min, please contact Web2Board support", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Link", "Status:", None, QtGui.QApplication.UnicodeUTF8))
        self.tryAgain.setText(QtGui.QApplication.translate("Link", "Try again", None, QtGui.QApplication.UnicodeUTF8))
        self.close.setText(QtGui.QApplication.translate("Link", "Close", None, QtGui.QApplication.UnicodeUTF8))

