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
import urllib2
import glob2
import serial.tools.list_ports

log = logging.getLogger(__name__)


def are_we_frozen():
    # All of the modules are built-in to the interpreter, e.g., by py2exe
    return hasattr(sys, "frozen")


def get_module_path(frame=None):
    encoding = sys.getfilesystemencoding()
    encoding = encoding if encoding is not None else 'utf-8'
    if not are_we_frozen():
        frame = frame if frame is not None else inspect.currentframe().f_back
        info = inspect.getframeinfo(frame)
        fileName = info.filename
        return os.path.dirname(os.path.abspath(unicode(fileName, encoding)))
    else:
        return os.path.dirname(os.path.abspath(unicode(sys.executable, encoding)))


def copytree(src, dst, filter_func=None, ignore=None, force_copy=False):
    if filter_func is None:
        filter_func = lambda x: True
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        if ignore is not None and ignore in item:
            continue
        s = os.path.join(src, item)

        if not filter_func(s):
            continue
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, filter_func, ignore, force_copy)
        else:
            if force_copy or not os.path.exists(d) or os.stat(s).st_mtime - os.stat(d).st_mtime > 1:
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


def list_directories_in_path(path):
    return [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]


def find_files(path, patterns):
    if not isinstance(patterns, (list, tuple, set)):
        patterns = [patterns]
    files = []
    for pattern in patterns:
        files += glob2.glob(path + os.sep + pattern)
    return list(set(files))


def find_files_for_pyinstaller(path, patterns):
    files = find_files(path, patterns)
    return [(f, f, 'DATA') for f in files if os.path.isfile(f)]


def find_modules_for_pyinstaller(path, patterns):
    files = find_files(path, patterns)

    def get_module_from_file(file):
        """
        :type file: str
        """
        module = file.replace(os.sep, ".")
        return module[:-3]  # removing .py

    list_modules = [get_module_from_file(f) for f in files if
                   os.path.isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")]
    return list(set(list_modules))


def extract_zip(origin, destination):
    with zipfile.ZipFile(origin, "r") as z:
        return z.extractall(destination)


def list_serial_ports(ports_filter=None):
    ports = list(serial.tools.list_ports.comports())
    if ports_filter is not None:
        ports = filter(ports_filter, ports)
    if is_mac():
        ports = ports + [[x] for x in glob('/dev/tty.*') if x not in map(lambda x: x[0], ports)]
    return list(ports)


def is_linux():
    return platform.system() == 'Linux'


def is_windows():
    return platform.system() == 'Windows'


def is_mac():
    return platform.system() == 'Darwin'


def is64bits():
    return sys.maxsize > 2 ** 32


def kill_process(name):
    name += get_executable_extension()
    if is_windows():
        try:
            os.system("taskkill /im {} -F".format(name))
        except:
            log.exception("Failing killing old web2board process")
    else:
        # check whether the process name matches
        try:
            os.system("killall -9 {}".format(name))
        except:
            log.exception("Failing killing old web2board process")


def get_executable_extension(frozen=False):
    if not are_we_frozen() and not frozen:
        return ".py"
    if is_mac():
        return ""
    if is_windows():
        return ".exe"
    if is_linux():
        return ""


def set_log_level(log_level):
    log_levels = {"debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING,
                  "error": logging.ERROR, "critical": logging.CRITICAL}

    log_level = log_level if isinstance(log_level, int) else log_levels[log_level.lower()]
    logging.getLogger().handlers[0].level = log_level


def open_file(file_path):
    if isinstance(file_path, str):
        file_path = file_path.decode(sys.getfilesystemencoding())
    # file_path.encode(sys.getfilesystemencoding())
    if sys.platform == "win32":
        template = u'"{0}" {1}'
    else:
        if file_path[0] == "/":
            template = u"'{0}' {1}"
        else:
            template = u"'./{0}' {1}"
    os.popen(u'"{0}" {1}'.format(file_path, " ".join(sys.argv[1:])).encode(sys.getfilesystemencoding()))


def set_proxy(proxy):
    proxy = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
