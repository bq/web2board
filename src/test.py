from subprocess import call
import os

import sys
print "wola!!!"
from libs.utils import getModulePath

args = ['C:\Users\jorgarira\SoftwareProjects\web2board\src\scons.exe',
        '-Q',
        '-j 4',
        '--warn=no-no-parallel-support',
        '-f',
        'C:\\Users\\jorgarira\\SoftwareProjects\\web2board\\src\\res\\scons\\platformio\\builder\\main.py',
        'PIOENV=uno',
        'PLATFORM=atmelavr',
        'UPLOAD_PORT=COM7',
        'BOARD=uno',
        'FRAMEWORK=arduino',
        'BUILD_SCRIPT=C:\\Users\\jorgarira\\SoftwareProjects\\web2board\\src\\res\\scons\\platformio\\builder\\scripts\\atmelavr.py',
        'PIOPACKAGE_TOOLCHAIN=toolchain-atmelavr',
        'PIOPACKAGE_FRAMEWORK=framework-arduinoavr',
        "upload"]

os.chdir("C:\Users\jorgarira\AppData\Roaming\web2board\platformio")

os.chdir("C:\Users\jorgarira\SoftwareProjects\web2board\src\Test\\resources\platformio")

sys.argv[1:] = args[1:]
#_null call(args)
sys.path.extend(['C:\Users\jorgarira\SoftwareProjects\web2board\src\\res\scons'])
execfile(getModulePath() + "\\res\Scons\scons.py")