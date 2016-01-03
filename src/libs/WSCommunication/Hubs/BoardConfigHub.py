from wshubsapi.Hub import Hub

from libs.CompilerUploader import getCompilerUploader, CompilerException, ERROR_BOARD_NOT_SUPPORTED
from libs.LibraryUpdater import getLibUpdater
from libs.Packagers.Packager import Packager


class BoardConfigHubException(Exception):
    pass


class BoardConfigHub(Hub):
    def __init__(self):
        super(BoardConfigHub, self).__init__()
        self.compilerUploader = getCompilerUploader()

    def getVersion(self):
        #todo: check in bitbloq if this is what we want
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

        #todo: do we need to set the port here??
        try:
            port = self.compilerUploader.getPort()
            _sender.isSettingPort(port)
        except CompilerException:
            raise BoardConfigHubException('NO PORT FOUND')
        return True  # if return None, client is not informed that the request is done

    def setLibVersion(self, version):
        libUpdater = getLibUpdater()
        if libUpdater.getBitbloqLibsVersion() != version:
            libUpdater.setBitbloqLibsVersion(version)
            libUpdater.downloadLibsIfNecessary()
        return True