import json
from shutil import copytree

from libs.PathConstants import *

version = json.load(open(RES_CONFIG_PATH))["version"]

os.chdir("../")

packagePath = Web2BoardPaths.getPathForNewPackage(version)

if os.path.exists(packagePath):
    os.rmdir(packagePath)
os.makedirs(Web2BoardPaths.getPathForNewPackage(version))

os.rmdir("..{0}src{0}res".format(os.sep))

copytree("..{0}res{0}linux".format(os.sep), "..{0}src{0}res".format(os.sep))
copytree("..{0}res{0}common".format(os.sep), "..{0}src{0}res".format(os.sep))
