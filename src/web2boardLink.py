import os
import platform
import shutil
import sys

import psutil

import libs.utils as utils
from libs.PathsManager import PathsManager

extension = ""
if platform.system() == 'Darwin':
    extension = ".app"
elif platform.system() == 'Windows':
    extension = ".exe"

web2boardPath = '"' + os.path.join(PathsManager.SETTINGS_PATH, "web2board" + extension) + '"'

for proc in psutil.process_iter():
    # check whether the process name matches
    try:
        if proc.name() in ("web2board.exe", "web2board", "web2board.app"):
            print "killing a running web2board application"
            proc.kill()
    except psutil.ZombieProcess:
        pass

if len(sys.argv) > 1 and sys.argv[1].lower() == "factoryreset":
    shutil.rmtree(PathsManager.SETTINGS_PATH)
    print "Extracting web2board from zip file"
    utils.extractZip(utils.getModulePath() + os.sep + "web2board.zip", PathsManager.SETTINGS_PATH)
    # os.system(web2boardPath + " --afterInstall")
else:
    os.popen("C:\Users\jorgarira\AppData\Roaming\web2board\web2board.exe &")