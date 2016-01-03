import os
import sys
import unittest

from libs.PathsManager import PathsManager


def __runTests():
    PathsManager.moveInternalConfigToExternalIfNecessary()
    unittest.main(module=sys.modules[__name__])
    os._exit(1)

def runUnitTests():
    from Test.unit.testUtils import TestUtils
    from Test.unit.WSCommunication.Hubs.testCodeHub import TestCodeHub
    __runTests()

def runIntegrationTests():
    from Test.integration.testCompilerUploader import testCompilerUploader
    __runTests()