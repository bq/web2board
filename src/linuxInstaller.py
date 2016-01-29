#!/usr/bin/env python
# coding=utf-8
import os
import subprocess
import getpass
import sys
import click
import pwd

import time

from libs.Decorators.Asynchronous import asynchronous
from libs.PathsManager import PathsManager
from libs.Downloader import Downloader
from libs import utils

print """
-----------------------------
INSTALANDO WEB2BOARD PARA BITBLOQ. NO CERRAR
INSTALLING BITBLOQS WEB2BOARD. DO NOT CLOSE\n\n\n
-----------------------------
Instalando...
Installing..."""

userName = getpass.getuser()
downloadInfo = dict(currentSize=0, speed=0, totalSize=0, finished=False)
installationPath = "/opt/web2board"


def askForSudo():
    global euid
    euid = os.geteuid()
    if euid != 0:
        print "Script not started as root. Running sudo.."
        args = ['sudo', sys.executable] + sys.argv + [os.environ]
        # the next line replaces the currently-running process with the sudo
        os.execlpe('sudo', *args)


def addAllUsersToDialOut():
    allUsers = [p[0] for p in pwd.getpwall()]
    for user in allUsers:
        subprocess.call(["sudo", "adduser", user, "dialout"])


def downloadVersion():
    downloader = Downloader()
    showDownloadProgressBar()
    downloader.download("https://github.com/bq/web2board/archive/v1.0.0.zip",
                        infoCallback=updateDownloadInfo,
                        endCallback=setDownloadFinished).get()


@asynchronous()
def showDownloadProgressBar():
    global downloadInfo
    while downloadInfo["totalSize"] == 0:
        time.sleep(0.1)
    with click.progressbar(length=downloadInfo["totalSize"], label="Downloading") as bar:
        lastCurrent = 0
        while not downloadInfo["finished"]:
            bar.update(downloadInfo["currentSize"] - lastCurrent)
            lastCurrent = downloadInfo["currentSize"]
            time.sleep(0.5)


def updateDownloadInfo(currentSize, totalSize, percent):
    downloadInfo["totalSize"] = totalSize
    downloadInfo["currentSize"] = currentSize


def setDownloadFinished(*args):
    downloadInfo["finished"] = True

askForSudo()
# addAllUsersToDialOut()

# downloadVersion()

if not os.path.exists(installationPath):
    os.makedirs(installationPath)

utils.extractZip(PathsManager.RES_PATH + os.sep + "web2board.zip", installationPath)

subprocess.call(["sudo", "chmod", "-R", "+rwxrwxrwx",  installationPath])
raw_input("""
--------------------------------------------------
INSTALACIÓN TERMINADA CORRECTAMENTE. PUEDE CERRAR LA VENTANA
INSTALLATION SUCCESSFULLY FINISHED. YOU MAY CLOSE THE WINDOW
REINICIE EL ORDENADOR
REBOOT THE COMPUTER
--------------------------------------------------

Presiona intro para terminar
Press enter to finish
\n\n\n""")
