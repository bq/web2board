from wshubsapi.hub import Hub

from libs.Config import Config
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Updater import VersionInfo
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater
from libs.Version import Version


class VersionsHandlerHubException(Exception):
    pass


class VersionsHandlerHub(Hub):
    @staticmethod
    def get_version():
        return Version.web2board

    @staticmethod
    def set_lib_version(version):
        libUpdater = BitbloqLibsUpdater.get()
        versionInfo = VersionInfo(version, Config.bitbloq_libs_download_url_template.format(version=version))
        if libUpdater.isNecessaryToUpdate(versionToCompare=versionInfo):
            libUpdater.update(versionInfo)

    def set_web2board_version(self, version):
        w2bUpdater = Web2BoardUpdater.get()
        try:
            w2bUpdater.downloadVersion(version, self.__download_progress, self.__download_ended).get()
        except:
            self.clients.getSubscribedClients().downloadEnded(False)
            raise
        w2bUpdater.makeAnAuxiliaryCopy()
        w2bUpdater.runAuxiliaryCopy(version)

    def __download_progress(self, current, total, percentage):
        self.clients.getSubscribedClients().downloadProgress(current, total, percentage)

    def __download_ended(self, task):
        self.clients.getSubscribedClients().downloadEnded(True)