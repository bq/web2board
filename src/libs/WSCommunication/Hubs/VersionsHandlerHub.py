from wshubsapi.hub import Hub

from libs.Config import Config
from libs.Updaters.LibsUpdater import LibsUpdater
from libs.Updaters.Web2boardUpdater import Web2BoardUpdater
from libs.AppVersion import AppVersion


class VersionsHandlerHubException(Exception):
    pass


class VersionsHandlerHub(Hub):

    def __init__(self):
        super(VersionsHandlerHub, self).__init__()
        self.w2b_updater = Web2BoardUpdater()
        self.lib_updater = LibsUpdater()

    def get_version(self):
        self.w2b_updater.clear_new_versions()
        return AppVersion.web2board.version_string

    def get_lib_version(self):
        return AppVersion.libs.version_string

    def set_lib_version(self, version, url):
        if Config.check_libraries_updates:
            if self.lib_updater.is_necessary_to_update(version):
                self.lib_updater.update(version, url)
        else:
            return "Check libraries flag is false"

    def set_web2board_version(self, version):
        if Config.check_online_updates and version != AppVersion.web2board:
            try:
                self.w2b_updater.download_version(version, self.__download_progress).result()
                self.__download_ended(True)
            except Exception as e:
                self.__download_ended(str(e))
                raise
            return True
        return False

    def __download_progress(self, current, total, percentage):
        self.clients.get_subscribed_clients().download_progress(current, total, percentage)

    def __download_ended(self, success):
        self.clients.get_subscribed_clients().downloadEnded(success)