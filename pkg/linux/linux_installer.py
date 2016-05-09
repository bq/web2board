#!/usr/bin/env python
# coding=utf-8
import os
import subprocess
import sys
import logging
import pwd

import click

from libs.PathsManager import PathsManager

BITBLOQS_HANDLER1 = """

#custom handler for bitbloqs web2board:
x-scheme-handler/web2board=web2board-handler.desktop
"""
BITBLOQS_HANDLER2 = """

#custom handler for bitbloqs web2board:
x-scheme-handler/web2board=web2board-handler.desktop
#END_WEB2BOARD_HANDLER
"""

DESKTOP_TEXT = """[Desktop Entry]
Version=2.0.1
Type=Application
Icon=/opt/web2board/web2board/res/Web2board.ico
Exec=/opt/web2board/web2boardLink
StartupNotify=true
Terminal=false
Categories=Utility;X-XFCE;X-Xfce-Toplevel
MineType=x-scheme-handler/vnc
Comment=Launch web2board
Name=Web2board Launcher
Name[en_US]=Web2board
"""

bash = 'bash -c \"echo INSTALLING BITBLOQS WEB2BOARD. DO NOT CLOSE; sudo {0} onTerminal;' \
       ' {0} factoryReset; exec bash\"'.format(sys.argv[0])


def startLogger():
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)
    # fileHandler = logging.FileHandler("installer.log", 'a')
    # fileHandler.setLevel(logging.DEBUG)
    # fileHandler.setFormatter(formatter)
    logger = logging.getLogger()
    # logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.DEBUG)
    return logging.getLogger(__name__)


def addAllUsersToDialOut():
    allUsers = [p[0] for p in pwd.getpwall()]
    for user in allUsers:
        subprocess.call(["sudo", "adduser", user, "dialout"], stdout=subprocess.PIPE)


def addHandlerInMimeapps():
    if not os.path.exists(applications_path):
        os.makedirs(applications_path)

    if os.path.isfile(mimeapps_file_path):
        with open(mimeapps_file_path) as f:
            f_content = f.read()
        f_content = f_content.replace(BITBLOQS_HANDLER2, "")
        f_content = f_content.replace(BITBLOQS_HANDLER1, "")
        if "[Default Applications]" not in f_content:
            f_content = "[Default Applications]\n" + f_content
        with open(mimeapps_file_path, "w") as f:
            f.write(f_content)

    with open(mimeapps_file_path, 'a') as f:
        f.write(BITBLOQS_HANDLER2)

    with open(web2board_desktop, "w") as f:
        f.write(DESKTOP_TEXT)
    os.system("chmod 777 '{}'".format(web2board_desktop))

applications_path = os.path.join(PathsManager.get_home_path(), ".local/share/applications")
mimeapps_file_path = os.path.join(applications_path, "mimeapps.list")
web2board_desktop = os.path.join(applications_path, "web2board-handler.desktop")

if len(sys.argv) <= 1:
    os.system("gnome-terminal -e \'{}\'".format(bash))

elif sys.argv[1] == "onTerminal":
    print applications_path
    print mimeapps_file_path
    print web2board_desktop

    log = None
    try:
        log = startLogger()
        log.info("Script started")
        log.info("Adding users to dialout...")
        os.remove(web2board_desktop)
        addAllUsersToDialOut()
        log.info("Installing web2board")
        os.system("sudo dpkg -i '{}'".format(os.path.join(sys._MEIPASS, "web2board.deb")))
        log.info("Successfully installed web2board")
        log.info("executing factoryReset")
    except:
        if log:
            log.exception("Failed performing installer")
        raise
    log.info("web2board successfully installed")


elif sys.argv[1] == "factoryReset":
    log = startLogger()
    log.info("Adding handler in Mimeapps file: {}".format(mimeapps_file_path))
    addHandlerInMimeapps()
    subprocess.Popen("/opt/web2board/web2boardLink --factoryreset".split(),
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE).wait()
    if click.confirm("It is necessary to restart the computer, do you want to restart it now?"):
        os.system("reboot")
