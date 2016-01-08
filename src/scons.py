import zipfile
import os
import sys
from pprint import pprint

from libs.utils import getModulePath, areWeFrozen
from libs.PathsManager import PathsManager, MAIN_PATH

PathsManager.moveInternalConfigToExternalIfNecessary()

if areWeFrozen():
    with zipfile.ZipFile(MAIN_PATH + os.sep + "res" + os.sep + "res.zip", "r") as z:
        z.extractall(MAIN_PATH)

pprint(sys.argv)

# args = ['C:\Users\jorgarira\SoftwareProjects\web2board\src\scons.exe',
#         '-Q',
#         '-j 4',
#         '--warn=no-no-parallel-support',
#         '-f',
#         MAIN_PATH + os.sep + 'scons\\platformio\\builder\\main.py',
#         'PIOENV=uno',
#         'PLATFORM=atmelavr',
#         'UPLOAD_PORT=COM3',
#         'BOARD=diecimilaatmega328',
#         'FRAMEWORK=arduino',
#         'BUILD_SCRIPT=' + MAIN_PATH + os.sep + 'scons\\platformio\\builder\\scripts\\atmelavr.py',
#         'PIOPACKAGE_TOOLCHAIN=toolchain-atmelavr',
#         'PIOPACKAGE_FRAMEWORK=framework-arduinoavr',
#         "upload"]

sys.argv[5] = MAIN_PATH + os.sep + 'platformio\\builder\\main.py'
sys.argv[11] = 'BUILD_SCRIPT=' + MAIN_PATH + os.sep + 'platformio\\builder\\scripts\\atmelavr.py'

os.chdir("C:\SoftwareProjects\web2board\src\Test\\resources\platformio")

# _null call(args)
sys.path.extend([MAIN_PATH + os.sep + 'scons'])
execfile(MAIN_PATH + os.sep + "scons\scons.py")
