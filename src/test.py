import os
import subprocess

from libs.PathsManager import MAIN_PATH
from libs.utils import isWindows, isMac, isLinux, listSerialPorts
from platformio.platformioUtils import run
from platformio import exception, util
from platformio.util import get_boards


def getIniConfig(environment):
    """
    :type environment: str
    """
    with util.cd("Test/platformio"):
        config = util.get_project_config()

        if not config.sections():
            raise exception.ProjectEnvsNotAvailable()

        known = set([s[4:] for s in config.sections()
                     if s.startswith("env:")])
        unknown = set((environment,)) - known
        if unknown:
            raise exception.UnknownEnvNames(
                    ", ".join(unknown), ", ".join(known))

        for section in config.sections():
            envName = section[4:]
            if environment and envName and envName == environment:
                iniConfig = {k:v for k,v in config.items(section)}
                iniConfig["boardData"] = get_boards(iniConfig["board"])
                return iniConfig

def callAvrdude(args):
    if isWindows():
        cmd = os.path.join(MAIN_PATH, 'res', 'avrdude.exe ') + args
    elif isMac():
        avrPath =  MAIN_PATH + "/res/arduinoDarwin/hardware/tools/avr"
        cmd = avrPath +"/bin/avrdude -C " +  avrPath +"/etc/avrdude.conf "+args
    elif isLinux():
        cmd = "avrdude " + args
    else:
        raise Exception("Platform not supported")
    print cmd
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=(not isWindows()))
    output = p.stdout.read()
    err = p.stderr.read()
    print output
    print err
    return output, err

def searchPort(mcu, baudRate):
    portsToUpload = listSerialPorts(lambda x: "Bluetooth" not in x[0])
    availablePorts = map(lambda x: x[0], portsToUpload)
    if len(availablePorts) <= 0:
        return []
    portsToUpload = []
    for port in availablePorts:
        args = "-P " + port + " -p " + mcu + " -b " + str(baudRate) + " -c arduino"
        output, err = callAvrdude(args)
        if 'Device signature =' in output or 'Device signature =' in err:
            portsToUpload.append(port)
    return portsToUpload

options = getIniConfig("diemilanove")
ports = searchPort(options["boardData"]["build"]["mcu"], options["boardData"]["upload"]["speed"])


run(target=("upload",), environment=("uno",), project_dir= "Test/platformio")