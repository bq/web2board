
from libs.PathsManager import PathsManager


def run():
    PathsManager.moveInternalConfigToExternalIfNecessary()

if __name__ == '__main__':
    run()

