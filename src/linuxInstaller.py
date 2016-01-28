#!/usr/bin/env python
# coding=utf-8
import os
import subprocess
import getpass
import sys

from libs.PathsManager import PathsManager
from libs.Downloader import Downloader
from libs import utils

"""
sudo adduser $userName dialout
sudo apt-get -y install gdebi
read name
sudo gdebi --non-interactive web2board.deb
read name
echo $ "\n\n\n-------------------------------------------------- "
echo  "INSTALACIÓN TERMINADA. PUEDE CERRAR LA VENTANA "
echo  "INSTALLATION FINISHED. YOU MAY CLOSE THE WINDOW "
echo  "REINICIE EL ORDENADOR "
echo  "REBOOT THE COMPUTER "
echo $ "--------------------------------------------------\n\n\n "
sudo chown -R $userName ~/Arduino && read name'
"""

print "-----------------------------"
print "INSTALANDO WEB2BOARD PARA BITBLOQ. NO CERRAR "
print "INSTALLING BITBLOQS WEB2BOARD. DO NOT CLOSE\n\n\n"
print "-----------------------------"
print "Instalando..."
print "Installing..."

userName = getpass.getuser()

euid = os.geteuid()
if euid != 0:
    print "Script not started as root. Running sudo.."
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    # the next line replaces the currently-running process with the sudo
    os.execlpe('sudo', *args)

print 'Running. Your euid is', euid

# add all users to dialout gourp: awk -F: '$3 > 999 {print $1}' /etc/passwd | xargs -I USERNAME sudo usermod -A dialout USERNAME
# listing all users
# import pwd, grp
# for p in pwd.getpwall():
#     print p[0], grp.getgrgid(p[3])[0]

subprocess.call(["sudo", "adduser", userName, "dialout"])
subprocess.call(["sudo", "apt-get", "-y", "install", "gdedbi"])
subprocess.call(["sudo", "gdebi", "--non-interactive", "web2board.deb"])
subprocess.call(["sudo", "chown", "-R", userName, "~/Arduino"])

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
