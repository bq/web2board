import os
import unittest

import sys

from libs.LoggingUtils import initLogging

log = initLogging(__name__)

def __runTests(suite, reportTitle="report"):
    from Test import setConfigurationFilesForTest
    from Test.HTMLTestRunner import HTMLTestRunner
    from libs.PathsManager import PathsManager
    setConfigurationFilesForTest.run()
    reportPath = PathsManager.SETTINGS_PATH + os.sep + reportTitle + '.html'
    runner = HTMLTestRunner(stream=file(reportPath, 'wb'), title=" Web2Board " + reportTitle, verbosity=1)
    # runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)


def runUnitTests():
    from Test.unit.Updaters.testUpdater import TestUpdater
    from Test.unit.WSCommunication.Hubs.testBoardConfigHub import TestBoardConfigHub
    from Test.unit.WSCommunication.Hubs.testCodeHub import TestCodeHub
    from Test.unit.WSCommunication.Hubs.testSerialMonitorHub import TestSerialMonitorHub
    from Test.unit.testUtils import TestUtils

    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCodeHub))
    suite.addTests(unittest.makeSuite(TestBoardConfigHub))
    suite.addTests(unittest.makeSuite(TestSerialMonitorHub))
    suite.addTests(unittest.makeSuite(TestUpdater))
    suite.addTests(unittest.makeSuite(TestUtils))
    __runTests(suite, "unitTestReport")


def runIntegrationTests():
    from Test.integration.testCompilerUploader import TestCompilerUploader
    from Test.integration.testUtils import TestUtils
    from Test.integration.Updaters.testBitbloqLibsUpdater import TestBitbloqLibsUpdater
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestCompilerUploader))
    suite.addTests(unittest.makeSuite(TestUtils))
    suite.addTests(unittest.makeSuite(TestBitbloqLibsUpdater))
    __runTests(suite, "integrationTestReport")


def runAllTests():
    runUnitTests()
    runIntegrationTests()


if __name__ == '__main__':
    if len(sys.argv)>1:
        testing = sys.argv[1]
    else:
        testing = ""
    if testing == "unit":
        runUnitTests()
    elif testing == "integration":
        runIntegrationTests()
    elif testing == "all":
        runAllTests()
    # log.warning("exiting program...")
    #os._exit(1)