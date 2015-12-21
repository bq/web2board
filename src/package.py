import json
from shutil import copytree, rmtree, copy

from libs.PathConstants import *

version = json.load(open(RES_CONFIG_PATH))["version"]

packagePath = Web2BoardPaths.getPathForNewPackage(version)

if os.path.exists(packagePath):
    rmtree(packagePath)
os.makedirs(Web2BoardPaths.getPathForNewPackage(version))

rmtree("res")

copytree("..{0}res{0}linux".format(os.sep), "res")
copy("..{0}res{0}common".format(os.sep), "res")
