from wshubsapi.Hub import Hub

from libs.CompilerUploader import getCompilerUploader, CompilerException, ERROR_BOARD_NOT_SUPPORTED
from libs.Packagers.Packager import Packager
from libs.Updaters.BitbloqLibsUpdater import getBitbloqLibsUpdater
from libs.Updaters.Updater import VersionInfo


class BoardConfigHubException(Exception):
    pass


class BoardConfigHub(Hub):
    BITBLOQ_LIBS_URL_TEMPLATE = 'https://github.com/bq/bitbloqLibs/archive/v{}.zip'

    def __init__(self):
        super(BoardConfigHub, self).__init__()
        self.compilerUploader = getCompilerUploader()

    def getVersion(self):
        # todo: check in bitbloq if this is what we want
        return Packager().version

    def setBoard(self, board, _sender):
        """
        :param board: board type
        :type _sender: ConnectedClientsGroup
        """
        if not board or board == "undefined":
            raise BoardConfigHubException('BOARD UNDEFINED')

        _sender.isSettingBoard()
        try:
            self.compilerUploader.setBoard(board)
        except CompilerException as e:
            if e.code == ERROR_BOARD_NOT_SUPPORTED["code"]:
                raise BoardConfigHubException('NOT SUPPORTED BOARD')

        # todo: do we need to set the port here??
        try:
            port = self.compilerUploader.getPort()
            _sender.isSettingPort(port)
        except CompilerException:
            raise BoardConfigHubException('NO PORT FOUND')
        return True  # if return None, client is not informed that the request is done

    def setLibVersion(self, version):
        libUpdater = getBitbloqLibsUpdater()
        versionInfo = VersionInfo(version, self.BITBLOQ_LIBS_URL_TEMPLATE.format(version))
        if libUpdater.isNecessaryToUpdate(versionToCompare=versionInfo):
            libUpdater.update(versionInfo)
        return True
