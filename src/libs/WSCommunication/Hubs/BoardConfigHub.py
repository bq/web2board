from wshubsapi.Hub import Hub

from libs.CompilerUploader import getCompilerUploader
from libs.LibraryUpdater import getLibUpdater


class BoardConfigHubException(Exception):
    pass


class BoardConfigHub(Hub):
    def __init__(self):
        super(BoardConfigHub, self).__init__()
        self.compilerUploader = getCompilerUploader()

    def getVersion(self):
        return self.compilerUploader.getVersion()

    def setBoard(self, board, _sender):
        """
        :param board: board type
        :type _sender: ConnectedClientsGroup
        """
        if board == "undefined":
            raise BoardConfigHubException('BOARD UNDEFINED')
        if board not in self.compilerUploader.arduino.ALLOWED_BOARDS:
            raise BoardConfigHubException('NOT SUPPORTED BOARD')

        _sender.isSettingBoard()
        port = self.compilerUploader.setBoard(board)

        if len(port) > 0:
            _sender.isSettingPort(port)
        else:
            raise BoardConfigHubException('NO PORT FOUND')
        return True  # if return None, client is not informed that the request is done

    def setPort(self, port):
        self.compilerUploader.setPort(port)
        return True

    def setLibVersion(self, version):
        libUpdater = getLibUpdater()
        if libUpdater.getBitbloqLibsVersion() != version:
            libUpdater.setBitbloqLibsVersion(version)
            libUpdater._downloadLibs()
        return True