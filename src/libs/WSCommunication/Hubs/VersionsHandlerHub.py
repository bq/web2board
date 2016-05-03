from wshubsapi.hub import Hub

from libs.Config import Config
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Updaters.Updater import VersionInfo
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater
from libs.Version import Version


class VersionsHandlerHubException(Exception):
    pass


class VersionsHandlerHub(Hub):

    def __init__(self):
        super(VersionsHandlerHub, self).__init__()
        self.w2b_updater = Web2BoardUpdater()
        self.libUpdater = BitbloqLibsUpdater()

    @staticmethod
    def get_version():
        return Version.web2board

    def set_lib_version(self, version):
        versionInfo = VersionInfo(version, Config.bitbloq_libs_download_url_template.format(version=version))
        if self.libUpdater.isNecessaryToUpdate(versionToCompare=versionInfo):
            self.libUpdater.update(versionInfo)

    def set_web2board_version(self, version):
        try:
            self.w2b_updater.downloadVersion(version, self.__download_progress, self.__download_ended).get()
        except:
            self.clients.get_subscribed_clients().downloadEnded(False)
            raise
        self.w2b_updater.makeAnAuxiliaryCopy()
        self.w2b_updater.runAuxiliaryCopy(version)

    def __download_progress(self, current, total, percentage):
        self.clients.get_subscribed_clients().downloadProgress(current, total, percentage)

    def __download_ended(self, task):
        self.clients.get_subscribed_clients().downloadEnded(True)