# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_LinuxInstaller.ui'
#
# Created: Fri Jan 29 12:44:28 2016
#      by: pyside-uic 0.2.15 running on PySide 1.2.4
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_LinuxInstallerWindow(object):
    def setupUi(self, LinuxInstallerWindow):
        LinuxInstallerWindow.setObjectName("LinuxInstallerWindow")
        LinuxInstallerWindow.resize(602, 154)
        self.centralwidget = QtGui.QWidget(LinuxInstallerWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.intro = QtGui.QLabel(self.centralwidget)
        self.intro.setObjectName("intro")
        self.verticalLayout_2.addWidget(self.intro)
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
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.install = QtGui.QPushButton(self.centralwidget)
        self.install.setObjectName("install")
        self.horizontalLayout.addWidget(self.install)
        self.cancel = QtGui.QPushButton(self.centralwidget)
        self.cancel.setObjectName("cancel")
        self.horizontalLayout.addWidget(self.cancel)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        LinuxInstallerWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(LinuxInstallerWindow)
        QtCore.QMetaObject.connectSlotsByName(LinuxInstallerWindow)

    def retranslateUi(self, LinuxInstallerWindow):
        LinuxInstallerWindow.setWindowTitle(QtGui.QApplication.translate("LinuxInstallerWindow", "Web2board", None, QtGui.QApplication.UnicodeUTF8))
        self.intro.setText(QtGui.QApplication.translate("LinuxInstallerWindow", "Thank you for using Web2board.\n"
"Click install to start the installation", None, QtGui.QApplication.UnicodeUTF8))
        self.updateGroupbox.setTitle(QtGui.QApplication.translate("LinuxInstallerWindow", "Installing", None, QtGui.QApplication.UnicodeUTF8))
        self.info.setText(QtGui.QApplication.translate("LinuxInstallerWindow", "Info:", None, QtGui.QApplication.UnicodeUTF8))
        self.install.setText(QtGui.QApplication.translate("LinuxInstallerWindow", "Install", None, QtGui.QApplication.UnicodeUTF8))
        self.cancel.setText(QtGui.QApplication.translate("LinuxInstallerWindow", "Cancel", None, QtGui.QApplication.UnicodeUTF8))

