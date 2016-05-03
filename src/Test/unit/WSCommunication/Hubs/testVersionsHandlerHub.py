import unittest

import sys
from PySide.QtGui import QApplication
from concurrent.futures import Future
from wshubsapi.hubs_inspector import HubsInspector
from wshubsapi.test.utils.hubs_utils import remove_hubs_subclasses

from Test.testingUtils import restoreAllTestResources, createCompilerUploaderMock, createSenderMock
from libs.Decorators.Asynchronous import Result
from libs.Updaters.BitbloqLibsUpdater import BitbloqLibsUpdater
from libs.Version import Version
from libs.WSCommunication.Hubs.VersionsHandlerHub import VersionsHandlerHub

# do not remove
import libs.WSCommunication.Hubs

from flexmock import flexmock, flexmock_teardown

try:
    QApplication(sys.argv)
except:
    pass


class TestVersionsHandlerHub(unittest.TestCase):
    def setUp(self):
        HubsInspector.inspect_implemented_hubs(force_reconstruction=True)
        Version.read_version_values()
        self.versionsHandlerHub = HubsInspector.get_hub_instance(VersionsHandlerHub)
        """ :type : VersionsHandlerHub"""
        self.libUpdater = self.versionsHandlerHub.lib_updater
        self.updater = self.versionsHandlerHub.w2b_updater
        self.sender = createSenderMock()

        self.compileUploaderMock, self.CompileUploaderConstructorMock = createCompilerUploaderMock()
        self.testLibVersion = "1.1.1"

        restoreAllTestResources()

    def tearDown(self):
        flexmock_teardown()
        remove_hubs_subclasses()

    def test_getVersion_returnsAVersionStringFormat(self):
        version = self.versionsHandlerHub.get_version()

        self.assertRegexpMatches(version, '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')

    def test_setLibVersion_doesNotDownloadLibsIfHasRightVersion(self):
        flexmock(self.libUpdater, isNecessaryToUpdate=lambda **kwargs: False).should_receive("update").never()
        self.libUpdater.currentVersionInfo.version = self.testLibVersion

        self.versionsHandlerHub.set_lib_version(self.testLibVersion)

    def test_setLibVersion_DownloadsLibsIfHasNotTheRightVersion(self):
        Version.bitbloq_libs = "0.0.1"
        self.libUpdater = flexmock(self.libUpdater).should_receive("update").once()

        self.versionsHandlerHub.set_lib_version(self.testLibVersion)

    def test_setLibVersion_returnsTrue(self):
        self.libUpdater = flexmock(self.libUpdater, update=lambda x: None)
        self.versionsHandlerHub.set_lib_version(self.testLibVersion)

    def test_setWeb2boardVersion_returnsTrue(self):
        result = Result(Future())
        result.future.set_result(True)
        flexmock(self.updater).should_receive("downloadVersion").and_return(result).once()
        flexmock(self.updater).should_receive("makeAnAuxiliaryCopy").once()
        flexmock(self.updater).should_receive("runAuxiliaryCopy").once()

        self.versionsHandlerHub.set_web2board_version("0.0.1")
