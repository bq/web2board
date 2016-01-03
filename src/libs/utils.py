import inspect
import json
import logging
import os
import platform
import shutil
import sys
import zipfile
from urllib2 import urlopen

import glob2
import serial.tools.list_ports
import libs.base

log = logging.getLogger(__name__)


def areWeFrozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def getModulePath(frame=None):
    encoding = sys.getfilesystemencoding()
    encoding = encoding if encoding is not None else 'utf-8'
    if not areWeFrozen():
        frame = frame if frame is not None else inspect.currentframe().f_back
        info = inspect.getframeinfo(frame)
        fileName = info.filename
        return os.path.dirname(os.path.abspath(unicode(fileName, encoding)))
    else:
        return os.path.dirname(os.path.abspath(unicode(sys.executable, encoding)))


def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)


def listDirectoriesInPath(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]


def findFilesForPyInstaller(path, patterns):
    if not isinstance(patterns, (list, tuple, set)):
        patterns = [patterns]
    files = []
    for pattern in patterns:
        files += glob2.glob(path + os.sep + pattern)
    return [(f, f, 'DATA') for f in files if os.path.isfile(f)]


def getUrlData(url):
    f = urlopen(url)
    return f.read()


def downloadFile(url):
    log.info("downloading " + url)
    urlData = getUrlData(url)
    tempFilePath = os.path.join(libs.base.sys_path.get_tmp_path(), os.path.basename(url))
    # Open our local file for writing
    with open(tempFilePath, "wb") as local_file:
        local_file.write(urlData)

    return tempFilePath


def extractZip(origin, destination):
    with zipfile.ZipFile(origin, "r") as z:
        z.extractall(destination)


def listSerialPorts(portsFilter=None):
    ports = list(serial.tools.list_ports.comports())
    if portsFilter is not None:
        ports = filter(portsFilter, ports)
    return ports


def isLinux():
    return platform.system() == 'Linux'


def isWindows():
    return platform.system() == 'Windows'


def isMac():
    return platform.system() == 'Darwin'
