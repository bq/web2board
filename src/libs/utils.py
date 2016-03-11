import inspect
import logging
import os
import platform
import shutil
import sys
import tempfile
import zipfile
from glob import glob
from urllib2 import urlopen
import glob2
import psutil
import serial.tools.list_ports
from datetime import datetime, timedelta

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


def copytree(src, dst, filter=None, ignore=None, forceCopy=False):
    if filter is None:
        filter = lambda x: True
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        if ignore is not None and ignore in item:
            continue
        s = os.path.join(src, item)

        if not filter(s):
            continue
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, filter, ignore, forceCopy)
        else:
            if forceCopy or not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
                shutil.copy2(s, d)

def rmtree(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except:
            log.exception("error removing file")


def listDirectoriesInPath(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]


def findFiles(path, patterns):
    if not isinstance(patterns, (list, tuple, set)):
        patterns = [patterns]
    files = []
    for pattern in patterns:
        files += glob2.glob(path + os.sep + pattern)
    return list(set(files))


def findFilesForPyInstaller(path, patterns):
    files = findFiles(path, patterns)
    return [(f, f, 'DATA') for f in files if os.path.isfile(f)]


def findModulesForPyInstaller(path, patterns):
    files = findFiles(path, patterns)

    def getModuleFromFile(file):
        """
        :type file: str
        """
        module = file.replace(os.sep, ".")
        return module[:-3]  # removing .py

    listModules = [getModuleFromFile(f) for f in files if
                   os.path.isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")]
    return list(set(listModules))


def getDataFromUrl(url):
    f = urlopen(url)
    return f.read()


def downloadFile(url, downloadPath=None):
    log.info("downloading " + url)
    extension = url.rsplit(".", 1)
    extension = extension[1] if len(extension) == 2 else ""
    urlData = getDataFromUrl(url)

    if downloadPath is None:
        downloadedTempFile = tempfile.NamedTemporaryFile(suffix="." + extension, delete=False)
    else:
        downloadedTempFile = open(downloadPath, "w")
    with downloadedTempFile:
        downloadedTempFile.write(urlData)

    return os.path.abspath(downloadedTempFile.name)


def extractZip(origin, destination):
    with zipfile.ZipFile(origin, "r") as z:
        return z.extractall(destination)


def listSerialPorts(portsFilter=None):
    ports = list(serial.tools.list_ports.comports())
    if portsFilter is not None:
        ports = filter(portsFilter, ports)
    if isMac():
        ports = set(ports + glob('/dev/tty.*'))
    return list(ports)


def isLinux():
    return platform.system() == 'Linux'


def isWindows():
    return platform.system() == 'Windows'


def isMac():
    return platform.system() == 'Darwin'


def is64bits():
    return sys.maxsize > 2 ** 32


def killProcess(name):
    name += getOsExecutableExtension()
    name = "web2board"
    def itWasCreatedJustBefore(proc):
        return datetime.now() - datetime.fromtimestamp(proc.create_time()) < timedelta(seconds=4)
    for proc in psutil.process_iter():
        # check whether the process name matches
        try:
            if name in proc.name() and proc.pid != os.getpid() and not itWasCreatedJustBefore(proc):
                log.debug("killing a running web2board application. old app pid: {0}, this pid {1}".format(proc.pid, os.getpid()))
                proc.kill()
        except psutil.ZombieProcess:
            pass
        except:
            log.exception("Failing killing old web2board process")


def getOsExecutableExtension():
    if not areWeFrozen():
        return ".py"
    if isMac():
        return ""
    if isWindows():
        return ".exe"
    if isLinux():
        return ""


def setLogLevel(logLevel):
    logLevels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
                 "error": logging.ERROR, "critical": logging.CRITICAL}

    logLevel = logLevel if isinstance(logLevel, int) else logLevels[logLevel.lower()]
    logging.getLogger().handlers[0].level = logLevel
